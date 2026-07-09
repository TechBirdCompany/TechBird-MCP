from devices.scope.siglent_sds2000xplus.siglent_sds2000xplus import Siglent_SDS2000
from devices.scope.rus_hmo3000.rus_hmo3000 import RUS_HMO3000
from devices.scope.rigol_mso1000.rigol_mso1000 import RIGOL_MSO1000

from devices.dmm.owon_xdm1000.owon_xdm_1000 import OWON_XDM1000
from devices.dmm.rigol_dmm800.rigol_dmm800 import RIGOL_DMM800

from devices.electronic_load.easttester_et54.easttester_et54 import EASTTESTER_ET54
from devices.electronic_load.peaktech_2275.peaktech_2275 import PeakTech_2275

from testcases.loadtest import load_test
import time
from loguru import logger

def main():

    #scope = Siglent_SDS2000("TCPIP0::10.10.10.90::INSTR")
    scope = RUS_HMO3000("TCPIP0::192.168.1.59::INSTR")

    #dmm = OWON_XDM1000()
    dmm = RIGOL_DMM800("TCPIP0::192.168.1.38::INSTR")

    #eload = EASTTESTER_ET54.auto_connect()
    eload = PeakTech_2275.auto_connect()

    load_test(
        scope=scope,
        dmm=dmm,
        eload=eload,
        voltage=5,
        max_voltage=5.05,
        min_voltage=4.95,
        domain="VCC5V0",
        current=0.5,
        single=True
    )

def fetch_rigol_screenshot(resource: str, filename: str = "rigol", suffix: str = "screenshot"):
    """Create a screenshot from the Rigol scope and return the saved path."""
    scope = RIGOL_MSO1000(resource)
    try:
        path = scope.save_screenshot(filename=filename, suffix=suffix)
        logger.info(f"Saved Rigol screenshot to {path}")
        return path
    finally:
        scope.close()

if __name__ == "__main__":

    fetch_rigol_screenshot(
        resource="TCPIP0::192.168.1.63::5555::SOCKET",
        filename="rigol_scope",
        suffix="capture"
    )

    main()