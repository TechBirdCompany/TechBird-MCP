from devices.scope.siglent_sds2000xplus.siglent_sds2000xplus import Siglent_SDS2000
from devices.scope.rus_hmo3000.rus_hmo3000 import RUS_HMO3000

from devices.dmm.owon_xdm1000.owon_xdm_1000 import OWON_XDM1000
from devices.dmm.rigol_dmm800.rigol_dmm800 import RIGOL_DMM800

from devices.electronic_load.easttester_et54.easttester_et54 import EastTester_ET54
from devices.electronic_load.peaktech_2275.peaktech_2275 import PeakTech_2275

from testcases.loadtest import load_test
import time
from loguru import logger


def main():

    #scope = Siglent_SDS2000("TCPIP0::10.10.10.90::INSTR")
    scope = RUS_HMO3000("TCPIP0::192.168.1.59::INSTR")

    #dmm = OWON_XDM1000()
    dmm = RIGOL_DMM800("TCPIP0::192.168.1.38::INSTR")

    #eload = EastTester_ET54.auto_connect()
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

if __name__ == "__main__":
    main()