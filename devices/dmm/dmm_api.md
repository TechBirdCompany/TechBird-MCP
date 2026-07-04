# DMM API Description

## Identify

```python
def identify():
    '''
    Identifies the device

    Returns:
        Result of ?IDN*
    '''
```

## Fetch Storage

```python
def fetch_storage(self, 
    samples: int = 200):
    '''
    Gets values for a given samples

    Args:
        samples:      Sets how many samples should be gathered or
                    how long the storage should be filled

    Returns:
        <VALUE>, <SAMPLE>
    '''
```

## Fetch Single

```python
def fetch_single(self):
    '''
    Gets the current value which is displayed on the screen

    Returns:
        Current measured value
    '''
```

## Clear

```python
def clear():
    '''
    Clears the current measurments and display
    '''
```

## Setup

```python
def setup(self, 
    mode: str = "V", 
    range: float = "230", 
    speed: str = "HIGH"):
    '''
    Configure the device to the desired settings

    Args:
        mode:   V(olt) or A(mpere)
        range:  Highest Voltage that should be measured
        speed:  LOW, MID or HIGH
    '''
```

## Set Display
```python
def set_display_statistics(self)
    '''
    Sets the device in a state for a statistical measurment
    ... how ever this looks like
    In best case sets the screen to a trend line and shows
    statistcs
    '''
```

## Get Screenshot
```python
def get_screenshot(self, 
    folder: str = "measurements", 
    prefix: str, 
    label: str):
    '''
    Get a screenshot of the current screen

    Args:
        folder:     Sets the folder where the screenshot should be saved
        time:       Includes a predefined time to make better mapping to other screenshots
        label:      Label of the measured value
    '''
```

## Get Plot
```python


def plot_storage(
    self,
    title: str,
    y_label: str,
    suffix: str = "",
    nominal_value: float = 0.0,
    min_limit: float = 0.0,
    max_limit: float = 0.0,
    limit: int = 10,
):
    """
    Creates a plot from measured samples and stores it as a PNG file.

    The required number of samples is acquired from the DMM and
    visualized together with nominal value and specification limits.

    Args:
        title: Plot title.
        y_label: Label for the y-axis.
        suffix: Optional filename prefix used for the generated PNG.
        nominal_value: Target/reference value displayed in the plot.
        min_limit: Lower specification limit.
        max_limit: Upper specification limit.
        limit: Number of samples to acquire before creating the plot.

    Returns:
        Path to the generated PNG file.
    """

```