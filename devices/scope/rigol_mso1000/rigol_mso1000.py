import os
import re
import socket
import time
from pathlib import Path
from typing import Literal

import pyvisa
from loguru import logger


class RIGOL_MSO1000:
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
    # SCPI Commands
    # ---------------------------

    def _scpi_identify(self) -> str:
        """
        Returns IDN
        """

        logger.debug(f"Querying IDN")

        return self.query("*IDN?")
    
    def _scpi_display_clear(self) -> None:
        """
        Clears Display
        """
        logger.info(f"Clear Display")
        
        self.write(":DISPlay:CLEar")

    def _scpi_display_persistence(
        self, 
        duration: Literal["MIN", "0.1", "0.2", "0.5", "1", "5", "10", "INFinite"] = "MIN"
    ) -> None:
        """
        Sets the duration of the persistence mode

        Args:
            <duration>  MIN|0.1|0.2|0.5|1|5|10|INFinite
        """
        logger.info(f"Set peristence time to {duration}")

        self.write(f":DISPlay:GRADing:TIME {duration}")

    def _scpi_acquire_type(
        self, 
        mode: Literal["NORMal", "AVERages", "PEAK", "HRESolution"] = "NORMAL"
    ) -> None:
        """
        Sets the acquire type of the scope

        Args:
            <mode>  NORMal|AVERages|PEAK|HRESolution
        """

        logger.inf(f"Set scope to acquire mode {mode}")

        self.write(f":ACQuire:TYPE {mode}")

    def _scpi_channel_display(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Enables given channel

        Args:
            <channel>   1|2|3|4
            <state> ON|OFF
        """

        logger.info(f"Sets channel {channel} to {state}")

        self.write(f":CHANnel{channel}:DISPlay {state}")

    def _scpi_channel_coupling(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        coupling: Literal["AC", "DC", "GND"] = "DC"
    ) -> None:
        """
        Sets coupling of given channel

        Args:
            <channel>   1|2|3|4
            <coupling>  AC|DC|GND
        """

        logger.info(f"Sets coupling of channel {channel} to {coupling}")

        self.write(f":CHANnel{channel}:COUPling {coupling}")

    def _scpi_channel_scale(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        volts_per_div: float = 10
    ) -> None:
        """
        Sets the volts per division of given channel

        Args:
            <channel>           1|2|3|4
            <volts_per_div>     float

        """

        logger.info(f"Sets channel {channel} to {volts_per_div} V/div")

        self.write(f":CHANnel{channel}:SCALe {volts_per_div}")

    def _scpi_channel_offset(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        offset: float = 0
    ) -> None:
        """
        Sets the offset for given channel

        Args:
            <channel>       1|2|3|4
            <offset>        float
        """

        logger.info(f"Sets channel {channel} to offset {offset}")

        self.write(f":CHANnel{channel}:OFFSet {offset}")

    def _scpi_channel_bandwidth(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        bandwidth_limit: Literal["20M", "OFF"] = "OFF"
    ) -> None:
        """
        Sets the bandwidth for given channel

        Args:
            <channel>   1|2|3|4
            <offset>    20M|OFF
        """

        logger.info(f"Sets channel {channel} bandwidth to {bandwidth_limit}")

        self.write(f":CHANnel{channel}:BWLimit {bandwidth_limit}")

    def _scpi_channel_probe(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        attenuation: Literal["0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1", "2", "5", "10", "20", "50", "100", "200", "500", "1000"] = 10
    ) -> None:
        """
        Sets the attenuation for given channel

        Args:
            <channel>       1|2|3|4
            <attenuation>   0.01|0.02|0.05|0.1|0.2|0.5|1|2|5|10|20|50|100|200|500|1000
        """

        logger.info(f"Set channel {channel} to attenuation {attenuation}")

        self.write(f":CHANnel{channel}:PROBe {attenuation}")

    def _scpi_channel_unit(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        unit: Literal["VOLTage", "WATT", "AMPere", "UNKNown"] = "VOLTage"
    ) -> None:
        """
        Sets the unit of given channel

        Args:
            <channel>       1|2|3|4
            <unit>          VOLTage|WATT|AMPere|UNKNown
        """
        logger.info(f"Set channel {channel} to {unit}")

        self.write(f":CHANnel{channel}:UNIT {unit}")

    def _scpi_trigger_edge_source(
        self, 
        channel: int
    ) -> None:
        """
        Sets the trigger source to given channel

        Args:
            <channel>       1|2|3|4            
        """

        logger.info(f"Set trigger to channel {channel}")

        self.write(f":TRIGger:EDGe:SOURce CHANnel{channel}")

    def _scpi_trigger_edge_level(self, level: float):
        """
        Set trigger level

        Args:
            <level>     float
        """

        logger.info(f"Set trigger level to {level}")

        self.write(f":TRIGger:EDGe:LEVel {level}")

    def _scpi_timebase_main_scale(
        self, 
        sec_per_div: float
    ) -> None:
        """
        Sets timebase

        Args:
            <sec_per_div>   
        """

        logger.info(f"Set Timebase to {sec_per_div}")

        self.write(f":TIMebase:MAIN:SCALe {sec_per_div}")

    def _scpi_measurement_clear(self) -> None:
        """
        Clears measurment
        """

        self.write(":MEASure:CLEar")

    def _scpi_measurement_statistics_display(
        self, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Activate statistics vor measurment
        """

        logger.info(f"Sets statistics measurment to {state}")

        self.write(f":MEASure:STATistic:DISPlay {state}")

    def _scpi_measurement_statistics_reset(self):
        """
        Resets statistics
        """

        logger.info(f"Resets statistics")

        self.write(":MEASure:STATistic:RESet")

    def _scpi_measurement_source(
        self, 
        channel: Literal[1, 2, 3, 4] = 1
    ) -> None:
        """
        Sets source for measurment

        Args:
            <channel>       1|2|3|4                    
        """

        logger.info(f"Set source of measurment")

        self.write(f":MEASure:SOURce CHANnel{channel}")

    def _scpi_measurement_item(
        self, 
        channel: int, 
        measurement_type: Literal["VMAX", "VMIN", "VPP", "VRMS"]
    ) -> None:
        """
        Choose the measurment item at given position

        Args:
            <channel>               1|2|3|4
            <measurment_type>       VMAX|VMIN|VPP|VTOP|VBASe|VAMP|VAVG|
                                    VRMS|OVERshoot|PREShoot|MARea|MPARea|
                                    PERiod|FREQuency|RTIMe|FTIMe|PWIDth|
                                    NWIDth|PDUTy|NDUTy|RDELay|FDELay|
                                    RPHase|FPHase|TVMAX|TVMIN|PSLEWrate|
                                    NSLEWrate|VUPper|VMID|VLOWer|VARIance|
                                    PVRMS|PPULses|NPULses|PEDGes|NEDGes
        """
        self.write(f":MEASure:ITEM {measurement_type},{channel}")

    def _scpi_run(self) -> None:
        """
        Sets the device in run mode
        """

        logger.debug(f"Starting acquisition")

        self.write(":RUN")

    def _scpi_stop(self) -> None:
        """
        Sets the device in stop mode
        """
        
        logger.debug(f"Stopping acquisition")

        self.write(":STOP")

    # ---------------------------
    # API Commands
    # ---------------------------

    def identify(
        self
    ) -> str:
        
        self._scpi_identify()

    def set_resolution(
        self,
        bit: Literal[8, 16] = 16
    ) -> None:
        
        if bin == 8:
            self._scpi_acquire_type(
                mode="NORMal"
            )
        else:
            self._scpi_acquire_type(
                model="HRESolution"
            )

    def set_channel(
        self,
        channel: Literal[1, 2, 3, 4] = 1,
        enable: Literal["ON", "OFF"] = "ON",
        attenuation: float = 10,
        unit: Literal["V", "A"] = "V",
        label: str = "",
        coupling: Literal["AC", "DC"] = "DC",
        bandwidth_limit: Literal["FULL", "20MHz"] = "FULL",
        volts_per_div: float = 5,
        position: float = 0
    ) -> None:
        pass    # no moode to add that....

    def set_trigger(
        self,
        channel: int,
        mode: str,
        level: float
    ) -> None:
        
        self._scpi_trigger_edge_source(
            channel=channel
        )

        self._scpi_trigger_edge_level(
            level=level
        )

    def set_timebase(
        self,
        sec_per_div: float
    ) -> None:
        pass    # Needs implementation

    def set_persistence(
        self,
        duration: float = 0
    ) -> None:
        
        if duration == 0:
            duration = "MIN"
        
        if duration == -1:
            duration = "INFinite"

        self._scpi_display_persistence(
            duration=duration
        )

    def reset(
        self
    ) -> None:

        pass    # needs implementation

    def set_measurement(
        self,
        position: Literal[1, 2, 3, 4, 5, 6] = 1,
        channel: Literal[1, 2, 3, 4] = 1,
        measurement_type: Literal["OFF", "MIN", "MAX", "PKPK", "RMS"] = "OFF"
    ) -> None:

        pass    # needs implementatin

    def save_screenshot(
        self,
        filename: str = "TEMP",
        suffix: str = ""
    ) -> None:
        
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

    def run(
        self
    ) -> None:
        
        self._scpi_run()

    def stop(
        self
    ) -> None:
        
        self._scpi_stop()

    def get_count(
        self,
        position: Literal[1, 2, 3, 4, 5, 6] = 1
    ) -> int:
        pass    # Keine Ahnung wie das geht

    def persistence_clear(self) -> None:
        
        self._scpi_display_clear()