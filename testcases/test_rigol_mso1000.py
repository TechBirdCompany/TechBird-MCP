import unittest
from unittest.mock import Mock, patch

from devices.scope.rigol_mso1000.rigol_mso1000 import Rigol_MSO1000


class TestRigolMSO1000(unittest.TestCase):
    def test_set_channel_uses_expected_rigol_commands(self):
        with patch("pyvisa.ResourceManager") as resource_manager_cls:
            inst = Mock()
            resource_manager_cls.return_value.open_resource.return_value = inst

            scope = Rigol_MSO1000("TCPIP0::192.168.1.63::INSTR")
            scope.set_channel(
                channel=1,
                enable=True,
                attenuation=10,
                unit="V",
                label="CH1",
                coupling="DC",
                bandwidth_limit="20MHz",
                volts_per_div=1.0,
                position=0.0,
            )

            commands = [call.args[0] for call in inst.write.call_args_list]
            self.assertIn(":CHANnel1:DISPlay ON", commands)
            self.assertIn(":CHANnel1:COUPling DC", commands)
            self.assertIn(":CHANnel1:SCALe 1.0", commands)
            self.assertIn(":CHANnel1:OFFSet 0.0", commands)

    def test_set_resolution_uses_high_resolution_mode(self):
        with patch("pyvisa.ResourceManager") as resource_manager_cls:
            inst = Mock()
            resource_manager_cls.return_value.open_resource.return_value = inst

            scope = Rigol_MSO1000("TCPIP0::192.168.1.100::INSTR")
            scope.set_resolution(10)

            commands = [call.args[0] for call in inst.write.call_args_list]
            self.assertIn(":ACQuire:TYPE HRESolution", commands)


if __name__ == "__main__":
    unittest.main()
