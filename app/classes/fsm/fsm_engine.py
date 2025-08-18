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
        """Émet un message ATC + attache thread_id + appelle le hook on_emit."""
        if not msgs:
            return

        m = choice(msgs)
        log_entry_dict = m.log_entry.to_dict()

        # au 1er log emis (ouverture du thread de communication)
        if self.thread_id is None:
            self.thread_id = log_entry_dict.get("id")

        if trans:
            log_entry_dict["acceptable_responses"] = self._get_formatted_response(trans)
            log_entry_dict["response_required"] = "Y" if trans.next_state is not "end" else "N" #BUG ICIIIIIIIII !!!!!!!!!!!!
            print(f"{"Y" if trans.next_state is not "end" else "N"}")

        payload = {
            "log_entry": log_entry_dict,
            "thread_id": self.thread_id,  # <- indispensable pour le manager
        }

        # 4) Notifier le manager pour qu'il indexe thread_id -> instance
        if self._on_emit:
            try:
                self._on_emit(payload)
            except Exception:
                # Ne bloque pas le flux si un observateur plante
                pass

        self.socket.send("scenario_log_add", payload, room=self.room)

    def _get_formatted_response(self, trans: Transition):
        """Construit la liste des réponses acceptables (branches d’abord, sinon expected explicite)."""
        responses = []
        if trans.branches:
            for ref in trans.branches.keys():
                dl = self.mongodb.find_datalink_by_ref(ref)
                if dl:
                    responses.append({"ref": ref, "text": dl.get("Message_Element")})
        elif isinstance(trans.expected, str) and trans.expected not in ("__ANY__", ""):
            dl = self.mongodb.find_datalink_by_ref(trans.expected)
            if dl:
                responses.append({"ref": trans.expected, "text": dl.get("Message_Element")})
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
            expected = trans.expected
            matched = (expected == "__ANY__") or (pilot_ref == expected)
            if not matched:
                print(f"EXPECTED MISMATCH: got {pilot_ref}, expected {expected}")
                return

            # atc_replies
            # if trans.atc_replies:
            #     self._emit_atc(trans.atc_replies)
            # self._cancel_timer()

            # 4) Avancer
            if trans.next_state:
                self.state_id = trans.next_state
                nxt = self.scenario[self.state_id]
                if nxt.atc_opening:
                    self._emit_atc(nxt.atc_opening, nxt)
                self._arm_timeout(nxt)
            elif trans.branches:
                self._arm_timeout(trans)
            else:
                # Fin du scénario
                self.state_id = "end" if "end" in self.scenario else None
                if self.state_id:
                    end = self.scenario[self.state_id]
                    if end.atc_replies:
                        self._emit_atc(end.atc_replies)
                self._cancel_timer()
                self.state_id = None
                if self._on_end:
                    try:
                        self._on_end()
                    finally:
                        self.thread_id = None   # libère l’ID pour ce moteur
