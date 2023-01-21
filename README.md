# Oekofen API

## Usage

```python
import oekofen_api
import asyncio

client = oekofen_api.Oekofen("192.168.178.222", "eMlG")
asyncio.run(client.update_data())
asyncio.run(client.get_status())
asyncio.run(client.get_weather_temp())

quit()

```