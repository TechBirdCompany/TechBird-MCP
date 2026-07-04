# Oscilloscope API Description

## Identify

```python
def identify():
    '''
    Identifies the device

    Returns:
        Result of ?IDN*
    '''
```

## Set Resolution
```python
    def set_resolution(self, bit="8Bits"):
        """
        Set the acquisition resolution to 10-bits or 8-bits.
        bit: "10bits" or "8bits"
        """
```

## Set Channel

```python
def set_channel(
    channel: int,
    enable: bool,
    attenuation: float,
    unit: str,
    label: str,
    coupling: str,
    bandwidth_limit: bool,
    scale: float,
    position: float,
):
    """
    Configures a channel.

    Args:
        channel: Channel number.
        enable: Show or hide channel.
        attenuation: Probe attenuation (1x, 10x, 100x ...).
        unit: V, A, W, ...
        label: Channel label.
        coupling: DC, AC, GND.
        bandwidth_limit: Enable bandwidth limit.
        scale: Vertical scale per division.
        position: Vertical position.
    """
```

## Set Trigger

```python    
def set_trigger(
    channel: int,
    mode: str,
    level: float,
):
    """
    Configures edge trigger.

    Args:
        channel: Trigger source.
        mode: Trigger mode.
        level: Trigger level.
    """
```

## Set Timebase

```python
def set_timebase(
    scale: float,
):
    """
    Configures horizontal scale.

    Args:
        scale: Time per division.
    """
```

## Set Persistence

```python
def set_persistence(
    time: float,
):
    """
    Enables display persistence.

    Args:
        time: Persistence duration in seconds.
    """
```

## Reset Display

```python
def reset_display():
    """
    Clears persistence,
    statistics and measurements.
    """
```

## Set Measurment

```python
def set_measurement(
    place: int,
    channel: int,
    measurement_type: str,
):

    """
    Adds a measurement to the screen.

    Args:
        place: Measurement slot.
        channel: Channel 1 to 4 for most scopes
        measurement_type:
            VMAX
            VMIN
            VPP
            VRMS
            FREQ
            PERIOD
            DUTY
            ...
    """
```

## Save Screenshot

```python
def save_screenshot(
    filename: str,
    suffix: str,
):
    """
    Saves a screenshot and returns
    the created file path.
    """
```

## Run

```python
def run():
    """
    Starts acquisition.
    """
```

## Stop

```python
def stop():
    """
    Stops acquisition.
    """
```

## Get Count

```python
    def get_count(
        position: int
    ):
        """
        Returns the count of saud position

        Args:
            positon: Measurment slot 1 to 5
        """
"""