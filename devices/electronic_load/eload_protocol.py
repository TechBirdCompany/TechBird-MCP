from typing import Protocol, Optional


class eload(Protocol):

    def identify(self):
        """
        Query device identification.
        """
        ...

    def load_on(self) -> None:
        """
        Enable electronic load.
        """
        ...

    def load_off(self) -> None:
        """
        Disable electronic load.
        """
        ...

    def get_load_state(self):
        """
        Query load state.
        """
        ...

    def set_mode(
        self,
        mode: str = "CC",
        channel: Optional[int] = None,
    ) -> None:
        """
        Configure operating mode.
        """
        ...

    def set_current(
        self,
        current: float,
        channel: Optional[int] = None,
    ) -> None:
        """
        Configure load current.
        """
        ...

    def fetch(
        self,
        channel: Optional[int] = None,
    ) -> Optional[tuple[float, float]]:
        """
        Read measurement values.

        Returns:
            (voltage, current)
        """
        ...

    def close(self) -> None:
        """
        Close connection.
        """
        ...