from typing import Protocol, Optional


class dmm(Protocol):

    def setup(
        self,
        mode: str = "V",
        range: float = 230,
        speed: str = "HIGH",
    ):
        """
        Configure the device.
        """
        ...

    def fetch_single(self) -> float:
        """
        Gets the current measurement value.
        """
        ...

    def fetch_storage(
        self,
        samples: int = 200,
    ):
        """
        Gets multiple measurement values.

        Returns:
            List of measured values.
        """
        ...

    def set_display(self) -> None:
        """
        Enables statistical display mode.
        """
        ...

    def get_screenshot(
        self,
        folder: str = "measurements",
        prefix: str = "",
        label: str = "",
    ):
        """
        Creates or retrieves a screenshot.

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
    ):
        """
        Creates a plot from stored measurements.

        Returns:
            Path to generated plot image.
        """
        ...
