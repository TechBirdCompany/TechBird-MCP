from typing import Protocol, Optional


class eload(Protocol):

    def identify(
        self
    ) -> str:
        """
        Query device identification.
        
        Returns:
            Result of *IDN?
        """
        ...

    def load_on(
        self
    ) -> None:
        """
        Enable electronic load.
        """
        ...

    def load_off(
        self
    ) -> None:
        """
        Disable electronic load.
        """
        ...

    def get_load_state(
        self
    ) -> bool:
        """
        Query load state.

        Returns:
            State of load 
            [TRUE = ON | FALSE = OFF]
        """
        ...

    def set_mode(
        self,
        mode: str = "CC",
        channel: Optional[int] = None,
    ) -> None:
        """
        Configure operating mode.

        Args:
            mode:       Mode of channel for eload
                        [CC]

            channel:    Optional parameter as most do have only one channel
                        But beside this; Number of channel
        """
        ...

    def set_current(
        self,
        current: float,
        channel: Optional[int] = None,
    ) -> None:
        """
        Configure load current.

        Args:
            current:    Set current for channel... as currently on CC is defined
                        This definition need to be changed, when other modes should
                        be supported
                        [CC]

            channel:    Optional parameter as most do have only one channel
                        But beside this; Number of channel
        """
        ...

    def fetch(
        self,
        channel: Optional[int] = None,
    ) -> tuple[float, float]:
        """
        Read measurement values.

        Args:
            channel:    Optional parameter as most do have only one channel
                        But beside this; Number of channel

        Returns:
            Returns volage and current, which are mostly the returned values in SCPI command guides
            [voltage, current]
        """
        ...

    def close(self) -> None:
        """
        Close connection.
        """
        ...