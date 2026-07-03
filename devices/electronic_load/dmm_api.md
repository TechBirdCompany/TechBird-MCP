# dmm_api Documentation

## Introduction
This document will descripe the needed functions to work globaly

## Functions

### identify(self)

Returns the identification string of the instrument.

```python
load.identify()
```

### load_on(self)

Switches the load on

```python
load.on()
```

### load_off(self)

Switches the load off

```python
load.off()
```

### set_mode(self, mode: str = "CC")

Sets the load into desired mode.

| Name | Type | Required | Allowed Values |
|--------|--------|----------|----------|
| mode | str | Yes | CC |

More modes can be available. Please see the respective manual

```python
load.set_mode(<mode>)
```

### set_current(self, current: float)

Sets the load to specified current

```python
load.set_current(<float>)
```

### fetch()

Gets the current values, should return
```
<voltage,current>
```

```python
load.fetch()
```
## Classmethod

### auto_connect()

Search for device and connect it
```python
<CLASS>.auto_connect()
```
