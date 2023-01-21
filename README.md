# Oekofen API

## Usage

- change `192.168.178.222` to your Oekofen IP
- change `eMlG` to your JSON Password (see Touchpad of your Oekofen)

```python
import oekofen_api
import asyncio

client = oekofen_api.Oekofen("192.168.178.222", "eMlG")
asyncio.run(client.update_data())
client.get_status()
client.get_weather_temp()
client.get_heating_circuit_temp()
asyncio.run(client.set_heating_circuit_temp(celsius=23))


```