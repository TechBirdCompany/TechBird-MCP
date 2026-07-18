from typing import Protocol, Literal, runtime_checkable

@runtime_checkable
class powersupply(Protocol):

    def identify(self) -> str:
        """
        Identifies the device.

        Returns:
            Result of *IDN?
        """
        ...
        
    def power_on_off(
        self,
        enable: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Powers channel on

        Args:
            <enable>   ON|OFF
        """
        ...

    def set_values(
        self,
        voltage: float = 0,
        current: float = 0
    ) -> None:
        """
        Sets voltage and current of power supply

        Args:
            <voltage>
            <current>
        """
        ...

    def get_value(
        self
    ) -> tuple[float, float]:
        """
        Gets voltage and current of power supply

        Returns:
            <voltage>, <current>
        """
        ...

    def lock(
        self,
        lock_enable: bool = False
    ) -> None:
        """
        Locks the power supply

        Args:
            <lock_enable>   TRUE|FALSE
        """
        ...