# Electronic Load API Description

## Identify

```python
def identify():
    '''
    Identifies the device

    Returns:
        Result of ?IDN*
    '''
```

## Fetch

```python
def fetch(self):
    '''
    Gets the current value which is displayed on the screen

    Returns:
        <VOLTAGE>, <CURRENT>
    '''
```

## Set Mode

```python
def set_mode(self, 
    mode: str = "CC, 
    channel: int = 1):
    '''
    Configure the device to the desired settings

    Args:
        mode:       "CC", "CV"
        channel:    Channel

    '''
```

## Set Current
```python
def set_current(self,
    current: float,
    channel: int = 1)
    '''
    Sets the desired current to channel

    Args:
        current:    Current for channel
        channel:    Channel
    '''
```

## On
```python
def load_on(self):
    '''
    Enable all channels
    '''
```

## Off
```python
def load_off(self):
    '''
    Disable all channels
    '''
```