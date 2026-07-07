from typing import Protocol, Optional


class dmm(Protocol):

    def setup(
        self,
        mode: str,
        range: float,
        speed: str,
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
    ):
        """
        Gets multiple measurement values.

        Args:
            samples:    Store for a number of samples before returning

        Returns:
            List of measured values.
        """
        ...

    def set_display(self) -> None:
        """
        Enables statistical display mode. Also kind of stupid function
        as it is hard to definy what should be done? What is the best screen?
        As an idea. Sets the display to given scneario like "statistic" or so.
        """
        ...

    def get_screenshot(
        self,
        folder: str = "measurements",
        prefix: str = "",
        label: str = "",
    ) -> str:
        """
        Creates or retrieves a screenshot.

        Args:
            folder: Folder for screenshot... should actually be hardcoded

            prefix: Should be suffix... but ads to the name for unified nameing

            label:  Label of the measured domain or signal

        Returns:
            File path or None.
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
    ) -> str:
        """
        Creates a plot from stored measurements.

        Args:
            title:          Title of the plit
            y_label:        y label...
            suffix:         suffix for the filename
            nominal_value:  Nominal value, will be displayed as center line
            min_limit:      Minimal limit
            max_limit:      Maximal limit
            limit:          Limits the plot to samples as it utilize the fetch_storage() function
                            Not sure if this is the smartest idea... or if the function
                            accepts an array or list

        Returns:
            Path to generated plot image.
        """
        ...
