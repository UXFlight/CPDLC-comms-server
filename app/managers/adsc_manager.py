import asyncio
from copy import deepcopy
import threading
from typing import Optional
import uuid
from app.classes.report.adsc_contract import ADSCContract
from app.utils.time_utils import get_current_timestamp


DEFAULT_ACTIVE_ADSC_CONTRACTS = [
    ADSCContract(id=str(uuid.uuid4()), center="CZQM001", period=180, time_Next=80, trigger="speed", is_active=True),
    ADSCContract(id=str(uuid.uuid4()), center="CZQM001", period=300, time_Next=120, trigger="position", is_active=True),
    ADSCContract(id=str(uuid.uuid4()), center="CZYZ003", period=300, time_Next=0, trigger="position", is_active=False)
]

class AdscManager:
    def __init__(self, socket, status, room, get_snapshot):
        self.socket = socket
        self.status = status
        self.room = room
        self._get_snapshot = get_snapshot

        self.adsc_contracts: list[ADSCContract] = deepcopy(DEFAULT_ACTIVE_ADSC_CONTRACTS)
        self.is_adsc_emergency = False

        self._adsc_lock = threading.Lock()
        self._adsc_stop = threading.Event()
        self._adsc_thread: Optional[threading.Thread] = None

    def adsc_to_dict(self):
        return [contract.to_dict() for contract in self.adsc_contracts]
    
        # adsc reports
    def real_period_based_on_acceleration(self, acceleration) -> float:
        for contract in self.adsc_contracts:
            contract.period = contract.period/acceleration
            contract.time_Next = contract.time_Next/acceleration
        print(f"ADSC contracts adjusted to acceleration {self.adsc_contracts}")

    def start_adsc_timer(self):
        if self._adsc_thread and self._adsc_thread.is_alive():
            return
        self._adsc_stop.clear()
        self._adsc_thread = threading.Thread(
            target=self._adsc_loop,
            name="ADSC-Timer",
            daemon=True,
        )
        self._adsc_thread.start()

    def stop_adsc_timer(self, join_timeout: float = 1.0):
        self._adsc_stop.set()
        t = self._adsc_thread
        if t and t.is_alive():
            t.join(timeout=join_timeout)
        self._adsc_thread = None

    # --- dans ReportsManager ---

    def stop_adsc(self):
        self._adsc_stop.set()

    async def stop_adsc_and_wait(self, timeout: float = 2.0):
        self.stop_adsc()
        t = self._adsc_thread
        if not t:
            return

        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout

        while t.is_alive() and loop.time() < deadline:
            await asyncio.sleep(0)

        if not t.is_alive():
            self._adsc_thread = None

    def _adsc_loop(self):
          while not self._adsc_stop.is_set():
            if self._adsc_stop.wait(timeout=1.0):
                break

            with self._adsc_lock:
                if not self._get_snapshot:
                    continue
                snap = self._get_snapshot()
                accel = snap.acceleration
                interval = snap.tick_interval
                updates_payload = []

                for c in self.adsc_contracts:
                    if not getattr(c, "is_active", False):
                        updates_payload.append(c.to_dict())
                        continue

                    try:
                        period = int(getattr(c, "period", 0))
                    except Exception:
                        period = 0
                    try:
                        tnext = int(getattr(c, "time_Next", 0))
                    except Exception:
                        tnext = 0

                    if tnext > 0:
                        tnext = max(0, tnext - (accel / interval))

                    if tnext == 0 and period > 0:
                        self._update_adsc_data(c, snap)
                        tnext = period

                    c.time_Next = tnext

                    updates_payload.append({
                        "id": c.id,
                        "center": c.center,
                        "period": c.period,
                        "time_Next": tnext,
                        "is_Active": c.is_active
                    })

                if updates_payload:
                    self.socket.send("adsc_countdown", updates_payload, room=self.room)
                    print(f"ADSC contracts updated: {updates_payload}")


    def _update_adsc_data(self, contract: ADSCContract, snap):
        match contract.trigger:
            case "speed":
                contract.add_data(time=get_current_timestamp(), value=self.status.speed)
            case "position":
                contract.add_data(time=get_current_timestamp(), value=snap.current_fix)
            case "altitude":
                contract.add_data(time=get_current_timestamp(), value=self.status.altitude)