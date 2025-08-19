# fsm_engine.py
import threading
from random import choice
from typing import List, Optional, Callable
from app.classes.fsm.fsm_types import Msg, Scenario, Transition
from app.managers.logs_manager.logs_manager import LogsManager

class FsmEngine:
    def __init__(
        self,
        socket,
        mongodb,
        room: str,
        scenario: Scenario = None,
        on_emit: Optional[Callable[[dict], None]] = None,  # <- NEW: hook (payload)
        on_end: Optional[Callable[[], None]] = None,       # <- NEW: hook fin
    ):
        self.socket = socket
        self.mongodb = mongodb
        self.room = room
        self.scenario = scenario

        self.state_id: Optional[str] = None
        self.thread_id: Optional[str] = None   # <- NEW: id du 1er log
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()

        self._on_emit = on_emit               # <- NEW
        self._on_end = on_end                 # <- NEW

    # ---------------- internals ----------------
    def _emit_atc(self, msgs: List[Msg], trans: Transition = None):
        if not msgs:
            return

        def _delayed_emit(): #delai de reponse simule
            m = choice(msgs)
            log_entry_dict = m.log_entry.to_dict()

            if self.thread_id is None:
                self.thread_id = log_entry_dict.get("id")

            if trans:
                next_state = trans.next_state
                next_trans = self.scenario[next_state] if next_state else None
                log_entry_dict["acceptable_responses"] = self._get_formatted_response(trans, next_trans)
                log_entry_dict["response_required"] = "Y" if next_state and next_state != "end" else "N"

            payload = {
                "log_entry": log_entry_dict,
                "thread_id": self.thread_id,
            }

            if self._on_emit:
                try:
                    self._on_emit(payload)
                except Exception:
                    pass

            self.socket.send("scenario_log_add", payload, room=self.room)

        threading.Timer(5.0, _delayed_emit).start()

    def _get_formatted_response(self, trans: Transition, next_trans: Transition):
        """Construit la liste des réponses acceptables (branches d’abord, sinon expected explicite)."""
        responses = []
        if trans.branches:
            for ref in trans.branches.keys():
                dl = self.mongodb.find_datalink_by_ref(ref)
                if dl:
                    responses.append({"ref": ref, "text": dl.get("Message_Element")})
        elif next_trans and isinstance(next_trans.expected, str) and next_trans.expected not in ("__ANY__", ""):
            dl = self.mongodb.find_datalink_by_ref(next_trans.expected)
            if dl:
                responses.append({"ref": next_trans.expected, "text": dl.get("Message_Element")})
        return responses

    def _cancel_timer(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _arm_timeout(self, trans: Transition):
        # """Arme un rappel STANDBY périodique tant que l'état n'avance pas."""
        # self._cancel_timer() # annuler le timer courant, pour eviter timer en parallele
        # if not trans.timeout_ms:  # si on veut des rappel, mettre timeout > 0, sinon mettre none ou 0
        #     return

        # def _on_timeout(): #callback execute quand le delai expire
        #     with self._lock:
        #         if self.state_id is None: #si le scenario termine/reinitialise entre temps on sort
        #             return
        #         self._emit_atc([ #renvoi le rappel car pas recu de reponse du pilote ????
        #             Msg(log_entry=LogsManager.create_log(self.mongodb, "UM1", "STANDBY."), role="ATC")
        #         ])
        #         self._arm_timeout(trans) #rearmement, donc rappel periodique

        # self._timer = threading.Timer(trans.timeout_ms / 1000.0, _on_timeout)
        # self._timer.daemon = True
        # self._timer.start()
        self._cancel_timer()
        return

    def set_scenario(self, scenario: Scenario):
        self.scenario = scenario

    def reset(self):
        """Réinitialise le moteur. Optionnel: prévenir le manager pour purge."""
        with self._lock:
            self._cancel_timer()
            self.state_id = None
            # Si tu veux que reset() purge aussi le mapping:
            if self._on_end and self.thread_id:
                try:
                    self._on_end()
                finally:
                    self.thread_id = None

    def enter(self, state_id: str):
        """Entrée dans un état (ex: 'atc_entry'). Émet l'ouverture et arme le timeout."""
        with self._lock:
            self._cancel_timer()
            self.state_id = state_id
            trans = self.scenario[state_id]
            if trans.atc_opening:
                self._emit_atc(trans.atc_opening, trans)
            self._arm_timeout(trans)

    def on_pilot_dm(self, pilot_ref: str, pilot_text: str = ""):
        """Traite le DM pilote. Branches -> expected -> réponses/avancement."""
        with self._lock:
            if not self.state_id or self.state_id not in self.scenario: #si state_id invalide ou vide
                if "pilot_entry" in self.scenario: # si nouveau scenario (donc initie par le pilote), etat par defaut pilot_entry
                    self.state_id = "pilot_entry"
                else:
                    # self._emit_atc([
                    #     Msg(log_entry=LogsManager.create_log(self.mongodb, "UM1", "STANDBY."), role="ATC")
                    # ])
                    print(f"INVALIDE STATE, FOR on_pilot_dm")
                    return

            trans = self.scenario[self.state_id]

            # branches
            if trans.branches and pilot_ref in trans.branches:
                nxt = trans.branches[pilot_ref]
                self._cancel_timer() # annuler le timer courant
                self.state_id = nxt
                nxt_trans = self.scenario[self.state_id]
                if nxt_trans.atc_replies:
                    self._emit_atc(nxt_trans.atc_replies, nxt_trans)
                self._arm_timeout(nxt_trans)
                return

            # expected
            next_state = trans.next_state
            next_trans = self.scenario[next_state] if next_state else None

            expected = next_trans.expected
            matched = (expected == "__ANY__") or (pilot_ref == expected)
            print(f"Pilot DM: {pilot_ref} (expected: {expected})")
            if not matched:
                print(f"EXPECTED MISMATCH: got {pilot_ref}, expected {expected}")
                return

            # si match on avance
            trans = next_trans

            # avancer
            if trans.next_state != "end":
                if trans.atc_replies:
                    self._emit_atc(trans.atc_replies, trans)
                self._arm_timeout(trans)
            else:
                self.state_id = "end" if "end" in self.scenario else None
                if self.state_id:
                    end = self.scenario[self.state_id]
                    if end.atc_replies:
                        self._emit_atc(end.atc_replies, trans)
                self._cancel_timer()
                self.socket.send("thread_ending",  self.thread_id, room=self.room)
                self.state_id = None
                if self._on_end:
                    try:
                        self._on_end()
                    finally:
                        self.thread_id = None   # libère l’ID pour ce moteur
