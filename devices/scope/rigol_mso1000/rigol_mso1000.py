import os
import re
import socket
import time
from pathlib import Path

import pyvisa
from loguru import logger


class Rigol_MSO1000:
    def __init__(self, resource):
        """
        resource examples:
        USB: 'USB0::0xF4EC::0xEE38::SDS1XXXX::INSTR'
        LAN: 'TCPIP0::192.168.1.100::INSTR'
        """
        self.rm = pyvisa.ResourceManager()
        self.inst = None
        self.sock = None
        self._resource = resource
        try:
            if isinstance(resource, str) and "SOCKET" in resource.upper():
                self.sock = self._open_socket(resource)
            else:
                self.inst = self.rm.open_resource(resource)
                self.inst.timeout = 5000
                self.inst.write_termination = "\n"
                self.inst.read_termination = "\n"
        except Exception as exc:
            logger.warning(f"Could not connect to Rigol MSO1000: {exc}")
            self.inst = None
            self.sock = None

    # ---------------------------
    # Basic communication
    # ---------------------------
    def _open_socket(self, resource):
        match = re.search(r"TCPIP0::([^:]+)::(\d+)::SOCKET", resource, re.IGNORECASE)
        if not match:
            raise ValueError(f"Unsupported Rigol socket resource: {resource}")
        host = match.group(1)
        port = int(match.group(2))
        sock = socket.create_connection((host, port), timeout=5)
        sock.settimeout(5)
        return sock

    def write(self, cmd):
        if self.sock is not None:
            try:
                self.sock.sendall((cmd + "\n").encode("ascii"))
                logger.info(f"Try command -> {cmd}")
            except Exception:
                logger.warning(f"Failure with command -> {cmd}")
            return

        if self.inst is None:
            logger.warning(f"No scope connection available for command -> {cmd}")
            return
        try:
            self.inst.write(cmd)
            logger.info(f"Try command -> {cmd}")
        except Exception:
            logger.warning(f"Failure with command -> {cmd}")

    def query(self, cmd):
        if self.sock is not None:
            try:
                self.sock.sendall((cmd + "\n").encode("ascii"))
                self.sock.settimeout(2)
                data = self.sock.recv(4096)
                if not data:
                    return ""
                return data.decode("ascii", errors="ignore").strip()
            except Exception as exc:
                logger.warning(f"Failure with command -> {cmd}: {exc}")
                return ""

        if self.inst is None:
            logger.warning(f"No scope connection available for query -> {cmd}")
            return ""
        try:
            return self.inst.query(cmd).strip()
        except Exception:
            logger.warning(f"Failure with command -> {cmd}")
            return ""

    def close(self):
        try:
            if self.sock is not None:
                self.sock.close()
            if self.inst is not None:
                self.inst.close()
            logger.info("Closing connection to Rigol MSO1000")
        except Exception:
            logger.warning("Failure closing connection to Rigol MSO1000")

    # ---------------------------
    # SCPI command helpers
    # ---------------------------
    def display_clear(self):
        self.write(":DISPlay:CLEar")

    def display_persistence(self, duration: float):
        if duration == 0:
            self.write(":DISPlay:GRADing:TIME 0")
        else:
            self.write(f":DISPlay:GRADing:TIME {duration}")

    def acquire_type(self, mode: str):
        self.write(f":ACQuire:TYPE {mode}")

    def channel_display(self, channel: int, state: bool):
        self.write(f":CHANnel{channel}:DISPlay {'ON' if state else 'OFF'}")

    def channel_coupling(self, channel: int, coupling: str):
        self.write(f":CHANnel{channel}:COUPling {coupling}")

    def channel_scale(self, channel: int, volts_per_div: float):
        self.write(f":CHANnel{channel}:SCALe {volts_per_div}")

    def channel_offset(self, channel: int, offset: float):
        self.write(f":CHANnel{channel}:OFFSet {offset}")

    def channel_bandwidth(self, channel: int, bandwidth_limit: str):
        self.write(f":CHANnel{channel}:BWLimit {bandwidth_limit}")

    def channel_label(self, channel: int, label: str):
        if label:
            self.write(f":CHANnel{channel}:LABel {label}")

    def channel_probe(self, channel: int, attenuation: float):
        self.write(f":CHANnel{channel}:PROBe {attenuation}")

    def channel_unit(self, channel: int, unit: str):
        self.write(f":CHANnel{channel}:UNIT {unit}")

    def trigger_edge_source(self, channel: int):
        self.write(f":TRIGger:EDGe:SOURce CHANnel{channel}")

    def trigger_edge_level(self, level: float):
        self.write(f":TRIGger:EDGe:LEVel {level}")

    def timebase_main_scale(self, sec_per_div: float):
        self.write(f":TIMebase:MAIN:SCALe {sec_per_div}")

    def measurement_clear(self):
        self.write(":MEASure:CLEar")

    def measurement_statistics_display(self, state: bool):
        self.write(f":MEASure:STATistic:DISPlay {'ON' if state else 'OFF'}")

    def measurement_statistics_reset(self):
        self.write(":MEASure:STATistic:RESet")

    def measurement_source(self, channel: int):
        self.write(f":MEASure:SOURce CHANnel{channel}")

    def measurement_item(self, position: int, measurement_type: str):
        self.write(f":MEASure:ITEM {position},{measurement_type}")

    def measurement_statistics_item(self, position: int):
        cmd = f":MEASure:STATistic:ITEM? {position}"
        logger.debug(f"Get count from statistics at position {position} -> {cmd}")
        return self.query(cmd)

    def run(self):
        cmd = ":RUN"
        logger.debug(f"Starting acquisition -> {cmd}")
        self.write(cmd)

    def stop(self):
        cmd = ":STOP"
        logger.debug(f"Stopping acquisition -> {cmd}")
        self.write(cmd)

    # ---------------------------
    # API methods
    # ---------------------------
    def identify(self):
        cmd = "*IDN?"
        logger.debug(f"Querying ID -> {cmd}")
        return self.query(cmd)

    def reset(self):
        """
        Clears persistence, statistics and measurements.
        """
        for i in range(1, 5):
            self.channel_display(i, False)

        self.measurement_clear()
        self.measurement_statistics_display(False)
        self.measurement_statistics_reset()
        self.display_clear()
        time.sleep(1)

    def set_resolution(self, bit: int):
        """
        Configure acquisition resolution.
        The Rigol DS/MSO1000Z series supports NORMal, AVERages, PEAK and HRESolution.
        """
        mode = "HRESolution" if bit >= 10 else "NORMal"
        logger.debug(f"Setting acquisition mode to {mode}")
        self.acquire_type(mode)

    def set_persistence(self, duration: float):
        """
        Configure display persistence.
        """
        self.display_persistence(duration)

    def set_channel(
        self,
        channel: int,
        enable: bool,
        attenuation: float,
        unit: str,
        label: str,
        coupling: str,
        bandwidth_limit: str,
        volts_per_div: float,
        position: float,
    ):
        """
        Configure a channel in the same style as the other scope wrappers.
        """
        if not enable:
            self.channel_display(channel, False)
            return

        self.channel_display(channel, True)
        self.channel_coupling(channel, coupling)
        self.channel_scale(channel, volts_per_div)
        self.channel_offset(channel, position)
        self.channel_bandwidth(channel, bandwidth_limit)
        self.channel_label(channel, label)
        self.channel_probe(channel, attenuation)
        self.channel_unit(channel, unit)

    def set_trigger(self, channel: int, mode: str, level: float):
        self.trigger_edge_source(channel)
        self.trigger_edge_level(level)

    def set_timebase(self, sec_per_div: float):
        self.timebase_main_scale(sec_per_div)

    def set_measurement(self, position: int, channel: int, measurement_type: str):
        if measurement_type == "OFF":
            self.measurement_item(position, "OFF")
            return

        self.measurement_source(channel)
        self.measurement_item(position, measurement_type)

    def get_count(self, position: int) -> float:
        return float(self.measurement_statistics_item(position))

    def save_screenshot(self, filename: str, suffix: str) -> str:
        os.makedirs("measurements", exist_ok=True)

        if filename:
            full_name = f"{filename}_SCOPE_{suffix}.png"
        else:
            full_name = f"SCOPE_{suffix}.png"

        path = Path("measurements") / full_name

        if self.sock is None and self.inst is None:
            logger.warning("No connection available to fetch Rigol screenshot")
            return str(path)

        if self.sock is not None:
            try:
                self.sock.sendall(b":DISPlay:DATA?\n")
                data = b""
                while True:
                    chunk = self.sock.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                    if len(data) > 8 and data.startswith(b"#"):
                        try:
                            n_digits = int(data[1:2])
                            length = int(data[2:2 + n_digits].decode("ascii"))
                            if len(data) >= 2 + n_digits + length:
                                data = data[2 + n_digits:2 + n_digits + length]
                                break
                        except Exception:
                            pass
                    if b"\n" in data and len(data) > 16:
                        break
                if data:
                    path.write_bytes(data)
                return str(path)
            except Exception as exc:
                logger.warning(f"Failed to fetch Rigol screenshot: {exc}")
                return str(path)

        try:
            self.inst.write(":DISPlay:DATA?")
            data = self.inst.read_raw()
        except Exception as exc:
            logger.warning(f"Failed to fetch Rigol screenshot: {exc}")
            return str(path)

        if data:
            path.write_bytes(data)
        return str(path)
