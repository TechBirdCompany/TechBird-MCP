#!/usr/bin/env python3.12
"""Quick test of ET54 measurement commands"""

import time
from devices.electronic_load.easttester_et54.easttester_et54 import EastTesterET54

try:
    load = EastTesterET54.auto_connect()
    print(f"Device: {load.idn['model']}")
    
    # Set to CC mode with 0.5A
    load.set_mode("CC", channel=1)
    load.set_current(0.5, channel=1)
    load.load_on()
    
    time.sleep(2)
    
    # Test measurements
    print("Testing measurements...")
    try:
        measurements = load.fetch(channel=1)
        print(f"✓ Measurements successful: V={measurements[0]:.2f}V, I={measurements[1]:.2f}A")
    except Exception as e:
        print(f"✗ Measurement failed: {e}")
    
    load.load_off()
    
finally:
    load.close()
