# scenario_manager.py
import threading
from typing import Dict, Optional
from app.classes.fsm.fsm_types import Scenario
from app.classes.fsm.fsm_engine import FsmEngine

class ScenarioInstance:
    def __init__(self, fsm: FsmEngine, room: str):
        self.fsm = fsm
        self.room = room
        self.lock = threading.Lock()

class FsmScenarioManager:
    def __init__(self, socket, mongodb):
        self.socket = socket
        self.mongodb = mongodb
        self._by_thread: Dict[str, ScenarioInstance] = {} # thread = thread de communication
        self._lock = threading.Lock()

    def start_scenario(
        self,
        scenario: Scenario,
        room: str,
        initiator: str = "ATC",
        pilot_ref: Optional[str] = None,
        pilot_text: str = "",
        thread_id: Optional[str] = None
    ) -> None:
        # Crée l'engine + l'instance (non indexée tant qu'on n'a pas le thread_id)
        fsm = FsmEngine(
            socket=self.socket,
            mongodb=self.mongodb,
            room=room,
            scenario=scenario,
            on_emit=None,  # défini juste après pour capturer `inst`
            on_end=None,
        )
        inst = ScenarioInstance(fsm=fsm, room=room)

        # Hook d'enregistrement au 1er emit (quand thread_id est connu)
        def _on_emit(payload: dict, inst=inst):
            thread_id = payload.get("thread_id")
            if not thread_id:
                return
            with self._lock:
                self._by_thread[thread_id] = inst

        # Hook de fin: purge par thread_id
        def _on_end(inst=inst):
            tid = inst.fsm.thread_id
            if not tid:
                return
            with self._lock:
                self._by_thread.pop(tid, None)

        fsm._on_emit = _on_emit
        fsm._on_end = _on_end

        if thread_id:
            print(f"N EST PAS SUPPOSE ENTRER ICI")
            fsm.thread_id = thread_id
            with self._lock:
                self._by_thread[thread_id] = inst

        # Démarre le scénario
        if initiator.upper() == "PILOT" and pilot_ref:
            fsm.on_pilot_dm(pilot_ref=pilot_ref, pilot_text=pilot_text)
        else:
            fsm.enter("atc_entry")

    def on_pilot_dm_by_thread(self, thread_id: str, pilot_ref: str, pilot_text: str = ""):
        with self._lock: #prendre le lock
            inst = self._by_thread.get(thread_id) # thread = id du premier log initiateur
        if not inst:
            return False # si thread inconnu, donc pas un scenario return
        with inst.lock:
            inst.fsm.on_pilot_dm(pilot_ref, pilot_text) # thread trouve = scenario actif = prendre le lock de l instance pui appel de la fct
        return True

    # (utile pour debug/observabilité)
    def get_active_threads(self):
        with self._lock:
            return {tid: inst.fsm.state_id for tid, inst in self._by_thread.items()}
