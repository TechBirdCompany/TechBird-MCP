import inspect

from devices.scope.scope_protocol import scope
from devices.scope.rus_hmo3000.rus_hmo3000 import RUS_HMO3000
from devices.scope.siglent_sds2000xplus.siglent_sds2000xplus import Siglent_SDS2000
from devices.scope.rigol_mso1000.rigol_mso1000 import RIGOL_MSO1000

from devices.dmm.dmm_protocol import dmm
from devices.dmm.owon_xdm1000.owon_xdm_1000 import OWON_XDM1000
from devices.dmm.rigol_dmm800.rigol_dmm800 import RIGOL_DMM800

from devices.electronic_load.eload_protocol import eload
from devices.electronic_load.easttester_et54.easttester_et54 import EastTester_ET54
from devices.electronic_load.peaktech_2275.peaktech_2275 import PeakTech_2275


DEVICES = [
    #(scope, RUS_HMO3000),
    #(scope, Siglent_SDS2000),
    (scope, RIGOL_MSO1000),

    #(dmm, OWON_XDM1000),
    #(dmm, RIGOL_DMM800),

    #(eload, EastTester_ET54),
    #(eload, PeakTech_2275),
]

def verify_protocol(protocol_cls, implementation_cls):

    protocol_methods = {
        name: obj
        for name, obj in inspect.getmembers(protocol_cls, inspect.isfunction)
        if not name.startswith("__")
    }

    missing = []
    mismatches = []
    ok = []

    for name, proto_method in protocol_methods.items():

        impl_method = getattr(implementation_cls, name, None)

        if impl_method is None:
            missing.append(name)
            continue

        proto_sig = inspect.signature(proto_method)
        impl_sig = inspect.signature(impl_method)

        proto_params = list(proto_sig.parameters.values())
        impl_params = list(impl_sig.parameters.values())

        if proto_params != impl_params:
            mismatches.append(name)
        else:
            ok.append(name)

    print(f"\n=== {implementation_cls.__name__} ===")

    for name in ok:
        print(f"✅ {name}")

    for name in missing:
        print(f"❌ Missing: {name}")

    for name in mismatches:
        print(f"⚠️ Signature mismatch: {name}")

    print(
        f"\nSummary: "
        f"{len(ok)} OK, "
        f"{len(missing)} Missing, "
        f"{len(mismatches)} Mismatches"
    )

    return len(missing) == 0 and len(mismatches) == 0

if __name__ == "__main__":
    for protocol_cls, implementation_cls in DEVICES:
        print(f"Checking {implementation_cls.__name__}...")
        verify_protocol(protocol_cls, implementation_cls)

    print("All protocol checks done")