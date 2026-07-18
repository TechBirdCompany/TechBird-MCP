from devices.scope.scope_protocol import scope
from devices.scope.rus_hmo3000.rus_hmo3000 import RUS_HMO3000
from devices.scope.siglent_sds2000xplus.siglent_sds2000xplus import SIGLENT_SDS2000
from devices.scope.rigol_mso1000.rigol_mso1000 import RIGOL_MSO1000

from devices.dmm.dmm_protocol import dmm
from devices.dmm.owon_xdm1000.owon_xdm_1000 import OWON_XDM1000
from devices.dmm.rigol_dmm800.rigol_dmm800 import RIGOL_DMM800

from devices.electronic_load.eload_protocol import eload
from devices.electronic_load.easttester_et54.easttester_et54 import EASTTESTER_ET54
from devices.electronic_load.peaktech_2275.peaktech_2275 import PEAKTECH_2275

from devices.powersupply.powersupply_protocol import powersupply
from devices.powersupply.peaktech_1885.peaktech_1885 import PEAKTECH_1885
from devices.powersupply.peaktech_6070.peaktech_6070 import PEAKTECH_6070
from devices.powersupply.korad_ka3000.korad_ka3000 import KORAD_KA3010DS

DEVICE_INFO = {

    # Scope
    "SIGLENT_SDS2000": {
        "protocol": scope,
        "class": SIGLENT_SDS2000,
    },

    "RUS_HMO3000": {
        "protocol": scope,
        "class": RUS_HMO3000,
    },

    "RIGOL_MSO1000": {
        "protocol": scope,
        "class": RIGOL_MSO1000,
    },

    # DMM
    "OWON_XDM1000": {
        "protocol": dmm,
        "class": OWON_XDM1000,
    },

    "RIGOL_DMM800": {
        "protocol": dmm,
        "class": RIGOL_DMM800,
    },

    # ELOAD
    "EASTTESTER_ET54": {
        "protocol": eload,
        "class": EASTTESTER_ET54,
        "auto": True,
    },

    "PEAKTECH_2275": {
        "protocol": eload,
        "class": PEAKTECH_2275,
        "auto": True,
    },

    # Power Supply
    "PEAKTECH_1885": {
        "protocol": powersupply,
        "class": PEAKTECH_1885,
        "auto": True,
    },

    "PEAKTECH_6070": {
        "protocol": powersupply,
        "class": PEAKTECH_6070,
        "auto": True,
    },

    "KORAD_KA3010DS": {
        "protocol": powersupply,
        "class": KORAD_KA3010DS,
        "auto": True,
    },
}