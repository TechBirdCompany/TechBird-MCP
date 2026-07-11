from devices.scope.siglent_sds2000xplus.siglent_sds2000xplus import Siglent_SDS2000
from devices.scope.rus_hmo3000.rus_hmo3000 import RUS_HMO3000
from devices.scope.rigol_mso1000.rigol_mso1000 import RIGOL_MSO1000

from devices.dmm.owon_xdm1000.owon_xdm_1000 import OWON_XDM1000
from devices.dmm.rigol_dmm800.rigol_dmm800 import RIGOL_DMM800

from devices.electronic_load.easttester_et54.easttester_et54 import EASTTESTER_ET54
from devices.electronic_load.peaktech_2275.peaktech_2275 import PEAKTECH_2275

from tools.test_load import test_load
from tools.get_visual import *
import time
from loguru import logger

def main():

    scope = Siglent_SDS2000("TCPIP0::10.10.10.90::INSTR")
    #scope = RUS_HMO3000("TCPIP0::192.168.1.59::INSTR")
    #scope = RIGOL_MSO1000("TCPIP0::192.168.1.63::5555::SOCKET")

    dmm = OWON_XDM1000()
    #dmm = RIGOL_DMM800("TCPIP0::192.168.1.38::INSTR")

    #eload = EASTTESTER_ET54.auto_connect()
    #eload = PEAKTECH_2275.auto_connect()

    """
    test_load(
        scope=scope,
        dmm=dmm,
        eload=eload,
        voltage=5,
        max_voltage=5.05,
        min_voltage=4.95,
        domain="VCC5V0",
        current=0.5,
        samples=20,
        single=True
    )
    """

    """
    get_screenshot_scope(
        device=scope,
        filename="Test",
        label_ch1="e1",
        label_ch2="2e",
        label_ch3="3r",
        label_ch4="4r"
    )
    """

    get_plot_dmm(
        device=dmm,
        filename="DMM",
        samples=20,
        title="Moep",
        y_label="V",
        nominal_value=5,
        min_limit=4.95,
        max_limit=5.05
    )

if __name__ == "__main__":
    main()