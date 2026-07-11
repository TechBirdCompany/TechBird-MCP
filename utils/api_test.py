import inspect
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from devices.scope.scope_protocol import scope
from devices.scope.rus_hmo3000.rus_hmo3000 import RUS_HMO3000
from devices.scope.siglent_sds2000xplus.siglent_sds2000xplus import Siglent_SDS2000
from devices.scope.rigol_mso1000.rigol_mso1000 import RIGOL_MSO1000

from devices.dmm.dmm_protocol import dmm
from devices.dmm.owon_xdm1000.owon_xdm_1000 import OWON_XDM1000
from devices.dmm.rigol_dmm800.rigol_dmm800 import RIGOL_DMM800

from devices.electronic_load.eload_protocol import eload
from devices.electronic_load.easttester_et54.easttester_et54 import EASTTESTER_ET54
from devices.electronic_load.peaktech_2275.peaktech_2275 import PEAKTECH_2275


DEVICES = [
    (scope, RUS_HMO3000),
    (scope, Siglent_SDS2000),
    (scope, RIGOL_MSO1000),

    (dmm, OWON_XDM1000),
    (dmm, RIGOL_DMM800),

    (eload, EASTTESTER_ET54),
    (eload, PEAKTECH_2275),
]

def verify_protocol(
    protocol_cls, 
    implementation_cls
) -> None:
    """
    Tests if the device classes provides every API function
    """

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

    return {
        "ok": len(ok),
        "missing": len(missing),
        "mismatches": len(mismatches),
    }

def run_api_test():

    summary = []

    for protocol_cls, implementation_cls in DEVICES:

        print(f"Checking {implementation_cls.__name__}...")

        result = verify_protocol(
            protocol_cls,
            implementation_cls
        )

        summary.append({
            "device": implementation_cls.__name__,
            **result
        })

    print("\n========== DEVICE OVERVIEW ==========")

    for entry in summary:

        issues = (
            entry["missing"]
            + entry["mismatches"]
        )

        print(
            f"{entry['device']:<25} "
            f"Error: {issues:<3} "
            f"(Missing={entry['missing']}, "
            f"Mismatch={entry['mismatches']})"
        )

    print("\nAll protocol checks done")


if __name__ == "__main__":
    run_api_test()
