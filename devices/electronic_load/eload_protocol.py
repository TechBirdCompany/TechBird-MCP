from typing import Protocol, Optional, Literal


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
        self,
        channel: Optional[Literal[1, 2]] = 1
    ) -> None:
        """
        Enable electronic load.
        """
        ...

    def load_off(
        self,
        channel: Optional[Literal[1, 2]] = 1
    ) -> None:
        """
        Disable electronic load.
        """
        ...

    def get_load_state(
        self,
        channel: Optional[Literal[1, 2]] = 1
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
        mode: Literal["CC"],
        channel: Optional[Literal[1, 2]] = 1
    ) -> None:
        """
        Configure operating mode.

        Args:
            <mode>      Mode of channel for eload
                        [CC]

            <channel>   Optional parameter as most do have only one channel
                        But beside this; Number of channel
        """
        ...

    def set_current(
        self,
        current: float,
        channel: Optional[Literal[1, 2]] = 1
    ) -> None:
        """
        Configure load current.

        Args:
            <current>    Set current for channel... as currently on CC is defined
                        This definition need to be changed, when other modes should
                        be supported
                        [CC]

            <channel>    Optional parameter as most do have only one channel
                        But beside this; Number of channel
        """
        ...

    def fetch(
        self,
        channel: Optional[Literal[1, 2]] = 1
    ) -> tuple[float, float]:
        """
        Read measurement values.

        Args:
            <channel>   Optional parameter as most do have only one channel
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