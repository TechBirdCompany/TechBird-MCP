from devices.scope.siglent_sds2000xplus import *

def load_test(voltage, current, duration):
    """
    Load test function to apply a specific voltage and current for a given duration.
    voltage: float value representing the voltage to be applied
    current: float value representing the current to be applied
    duration: float value representing the duration of the test [s]
    """

    # Connect to the oscilloscope
    scope = SiglentSDS("TCPIP0::10.10.10.90::INSTR")

    # Get the device ID and print it
    print(scope.get_id())

    # Configure the oscilloscope channels
    scope.set_channel_enable(1, True)
    scope.set_channel_enable(2, True)
    scope.set_channel_enable(3, False)
    scope.set_channel_enable(4, False)
    
    # Hide the menu and set the acquisition
    scope.display_hide_menu()
    
    # Set the acquisition mode to 10-bit
    scope.set_10bit_mode(True)

    # Set the coupling mode for channels 1 and 2 to DC
    scope.set_channel_coupling(1, "DC")
    scope.set_channel_coupling(2, "DC")

    # Set the attenuation for channels 1 and 2 
    scope.set_channel_attenuation(1, 10)
    scope.set_channel_attenuation(2, 1)

    # Set the label visibility and text for channels 1 and 2
    scope.set_channel_label_on_off(1, True)
    scope.set_channel_label_on_off(2, True)
    scope.set_channel_label_text(1, "VCC_1V0 Voltage")
    scope.set_channel_label_text(2, "VCC_1V0 Current")

    # Set the bandwidth limit for channels 1 and 2
    scope.set_channel_bwlimit(1, "2MHz")
    scope.set_channel_bwlimit(2, "20MHz")

    # Set the unit for channels 1 and 2
    scope.set_channel_unit_volt(1, True)
    scope.set_channel_unit_volt(2, False)

    # Set the vertical scale and offset for channels 1 and 2
    scope.set_channel_vertical_scale(1, 0.2)
    scope.set_channel_vertical_scale(2, 0.1)

    # Set the vertical offset for channels 1 and 2
    scope.set_channel_offset(1, 0.2*2*-1)
    scope.set_channel_offset(2, 0.1*3*-1)

    # Set the timebase for the oscilloscope
    scope.set_timebase(1/1000)

    # Set the trigger source and edge for the oscilloscope
    scope.set_trigger_edge_source(1)
    scope.set_trigger_edge(0)