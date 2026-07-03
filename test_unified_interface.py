#!/usr/bin/env python3
"""Test both ET54 and PeakTech with unified interface"""

import time
from devices.electronic_load.peaktech_2275.peaktech_2275 import PeakTech2275
from devices.electronic_load.easttester_et54.easttester_et54 import EastTesterET54

def test_device(device_class, name):
    """Test a device with the unified interface"""
    print(f"\n{'='*50}")
    print(f"Testing {name}")
    print('='*50)
    
    try:
        load = device_class.auto_connect()
        print(f"✓ Connected to {name}")
        
        # Identify device
        idn = load.identify()
        print(f"✓ Device ID: {idn}")
        
        # Set mode and current with unified interface
        load.set_mode("CC", channel=1)
        print(f"✓ Set mode to CC")
        
        load.set_current(0.5, channel=1)
        print(f"✓ Set current to 0.5A")
        
        # Enable load
        load.load_on()
        print(f"✓ Load enabled")
        
        time.sleep(2)
        
        # Read measurements with unified interface
        measurements = load.fetch(channel=1)
        if measurements:
            print(f"✓ Measurements: V={measurements[0]:.2f}V, I={measurements[1]:.2f}A")
        else:
            print(f"✗ Failed to read measurements")
        
        # Disable load
        load.load_off()
        print(f"✓ Load disabled")
        
        load.close()
        print(f"✓ Connection closed\n")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing {name}: {e}\n")
        return False

# Test both devices
print("UNIFIED INTERFACE TEST - Device Interchangeability")
print("Using identical code for both ET54 and PeakTech2275")

et54_ok = test_device(EastTesterET54, "EastTesterET54")
pt_ok = test_device(PeakTech2275, "PeakTech2275")

print("="*50)
print("SUMMARY:")
print(f"  ET54:       {'✓ PASS' if et54_ok else '✗ FAIL'}")
print(f"  PeakTech:   {'✓ PASS' if pt_ok else '✗ FAIL'}")
print("="*50)
