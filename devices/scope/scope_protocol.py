from typing import Protocol

class scope(Protocol):

    def identify(
        self
    ) -> str:
        """
        Identifies the device.

        Returns:
            Result of *IDN?
        """
        ...

    def set_resolution(
        self,
        bit: int,
    ) -> None:
        """
        Configure acquisition resolution.

        Args:
            bit:    Number of Bits. Function should be implemented in a way,
                    that the more matching bitrate is set.
                    i.E. bit=12 with an Siglent SDS2000X-Plus should result 
                    in a 10.Bit mode
                    [8+0.5*n <= 16]
        """
        ...

    def set_channel(
        self,
        channel: int,
        enable: bool,
        attenuation: float,
        unit: str,
        label: str,
        coupling: str,
        bandwidth_limit: str,
        volts_per_div: float,
        position: float,
    ) -> None:
        """
        Configures the channel

        Args:
            channel:            Channel 1 to 4
                                With a 2 CH Scope there should be a warning when
                                channel > 2 and abort the test
                                [1|2|3|4]

            enable:             Enables channel

            attenuation:        Atennuation of the channel

            unit:               Unit of the channel
                                [V|A]

            label:              Label of the channel
                                Function should take the max length into account
                                If label is to long, it should generate a warning and limit
                                the label to a matching length

            coupling:           Coupling of channel
                                [AC|DC]

            bandwidth_limit:    Sets the bandwidth limit
                                [FULL|20MHz]

            volts_per_div:      Sets the vertical scale as volts per devision... even with current

            position:           Position of the channel
        """
        ...

    def set_trigger(
        self,
        channel: int,
        mode: str,
        level: float,
    ) -> None:
        """
        Configure trigger settings.

        Args:
            channel:    Sets Trigger to Channel 1 to 4
                        With a 2 CH Scope there should be a warning when
                        channel > 2 and abort the test
                        [1|2|3|4]

            mode:       Sets trigger mode
                        [EDGE]

            level:      Level of the trigger
        """
        ...

    def set_timebase(
        self,
        sec_per_div: float,
    ) -> None:
        """
        Configure horizontal scale.
        
        Args:
            sec_per_div:    Sets the horizontal scale as seconds per division
        """
        ...

    def set_persistence(
        self,
        duration: float,
    ) -> None:
        """
        Configure display persistence.

        Args:
            duration:   Sets the duration of the presistance mode
                        0 should turn off persistance mode
        """
        ...

    def reset(
        self
    ) -> None:
        """
        Clears persistence,
        statistics and measurements.
        """
        ...

    def set_measurement(
        self,
        position: int,
        channel: int,
        measurement_type: str,
    ) -> None:
        """
        Configure measurement slot.

        Args:
            position:           Position of the measurment
                                If position is to high the function should create a warning

            channel:            Channel on which the measurment is performed

            measurment_type:    Type of the measurment
                                [PKPK|RMS|MAX|MIN]
        """
        ...

    def save_screenshot(
        self,
        filename: str,
        suffix: str,
    ) -> str:
        """
        Save screenshot and return path.

        Args:
            filename:   Filename of the screenshot

            suffix:     Additional suffix to unify with other screesnhots or so

        Returns:
            I don't know... maybe the path... can be removed with later revisions
        """
        ...

    def run(
        self
    ) -> None:
        """
        Starts acquisition.
        """
        ...

    def stop(
        self
    ) -> None:
        """
        Stops acquisition.
        """
        ...

    def close(
        self
    ) -> None:
        """
        Close connection.
        """
        ...

    def get_count(
        self,
        position: int
    ) -> int:
        """
        Returns the count of said position

        Args:
            position:   Position where the count should be taken off

        Returns:
            Integer of captured waveforms
        """

    def persistence_clear(self):
        """
        Clears the persistence traces from the display.
        """