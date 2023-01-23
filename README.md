# Oekofen API

## Usage

- change `192.168.178.222` to your Oekofen IP
- change `eMlG` to your JSON Password (see Touchpad of your Oekofen)

```python
import oekofen_api
import asyncio
import time

client = oekofen_api.Oekofen("192.168.178.222", "eMlG")
asyncio.run(client.update_data())
client.get_status()
client.get_weather_temp()
client.get_heating_circuit_temp()

old_value = client.get_attribute('pu', 'L_tpo_act').get_value()
print(old_value)
while True:
    try:
        asyncio.run(client.update_data())
    except Exception:
        time.sleep(5)
        continue
    new_value = client.get_attribute('pu', 'L_tpo_act').get_value()
    time.sleep(10)
    if new_value != old_value:
        print(old_value, new_value)
        old_value = new_value

#asyncio.run(client.set_heating_circuit_temp(celsius=23))


```


## Todo

- dont use `domains` and `attributes`- make it less complicate and pass dict to homeassistant, then use data scheme like netgear integration


## References

- https://github.com/JbPasquier/pyokofen/blob/master/pyokofen/okofen.py
- 