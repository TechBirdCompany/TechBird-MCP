from typing import Protocol, Optional, Literal


class dmm(Protocol):

    def setup(
        self,
        mode: Literal["V", "A"] = "V",
        range: float = 0,
        speed: Literal["SLOW", "MID", "FAST"] = "FAST",
    ) -> None:
        """
        Configure the device.

        Args:
            mode:   Sets the mode 
                    [V|A]
            
            range:  Range is kind of a stupid name and should be the
                    expected voltage which should be measured, as steps 
                    are different with every dmm
                    [0 = AUTO]

            speed:  Apperently most of DMMs do have speeds
                    [SLOW|MID|FAST]
        """
        ...

    def fetch_single(
        self
    ) -> float:
        """
        Gets the current measurement value.

        Returns:
            Returns the current value
        """
        ...
        
    def fetch_storage(
        self,
        samples: int = 200,
    ) -> list[float]:
        """
        Gets multiple measurement values.

        Args:
            samples:    Store for a number of samples before returning

        Returns:
            List of measured values.
        """
        ...

    def set_display(
        self,
        scenario: Literal["STAT"]
    ) -> None:
        """
        Enables verious scenarious

        Args:
            scenario:   STAT    sets the display to a statistic mode
        """
        ...

    def get_screenshot(
        self,
        folder: str = "measurements",
        prefix: str = "",
        label: str = "",
    ) -> None:
        """
        Retrieves a screenshot.

        Args:
            folder: Folder for screenshot... should actually be hardcoded

            prefix: Should be suffix... but ads to the name for unified nameing

            label:  Label of the measured domain or signal
        """
        ...

    def get_plot(
        self,
        title: str,
        y_label: str,
        suffix: str = "",
        nominal_value: float = 0.0,
        min_limit: float = 0.0,
        max_limit: float = 0.0,
        limit: int = 200,
    ) -> None:
        """
        Creates a plot from stored measurements.

        Args:
            title:          Title of the plit
            y_label:        y label...
            suffix:         suffix for the filename
            nominal_value:  Nominal value, will be displayed as center line
            min_limit:      Minimal limit
            max_limit:      Maximal limit
            limit:          Limit to use for the fetch_storage function
        """
        ...
