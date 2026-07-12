from devices.scope.scope_protocol import scope
from devices.scope.rus_hmo3000.rus_hmo3000 import (
    RUS_HMO3000
)
from devices.scope.siglent_sds2000xplus.siglent_sds2000xplus import (
    SIGLENT_SDS2000
)
from devices.scope.rigol_mso1000.rigol_mso1000 import (
    RIGOL_MSO1000
)

from devices.dmm.dmm_protocol import dmm
from devices.dmm.owon_xdm1000.owon_xdm_1000 import (
    OWON_XDM1000
)
from devices.dmm.rigol_dmm800.rigol_dmm800 import (
    RIGOL_DMM800
)

from devices.electronic_load.eload_protocol import eload
from devices.electronic_load.easttester_et54.easttester_et54 import (
    EASTTESTER_ET54
)
from devices.electronic_load.peaktech_2275.peaktech_2275 import (
    PEAKTECH_2275
)

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
}