# Oekofen API

## Usage

- change `192.168.178.222` to your Oekofen IP
- change `eMlG` to your JSON Password (see Touchpad of your Oekofen)

```python
import oekofen_api
import asyncio
import time

client = oekofen_api.Oekofen("192.168.178.222", "eMlG")
asyncio.run(client.update_csv_data())
asyncio.run(client.get_version())

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
- http://192.168.178.222:4321/eMlG/all?
- https://pypi.org/project/oekofen-api/
- https://developers.home-assistant.io/docs/core/entity/binary-sensor
- https://github.com/home-assistant/core/blob/master/homeassistant/components/binary_sensor/__init__.py
- http://0.0.0.0:8123/lovelace/0
- https://materialdesignicons.com/

## Berechnung Pelletsverbrauch

Berechnungsgrundlage: Abschnitt `Calculations` in [Oekofen-Spy](https://gitlab.com/p3605/oekofen-spy)

1. Ableitung `pe1_L_modulation` [via derivative](https://www.home-assistant.io/integrations/derivative/) minütlich
   1. siehe Integration [derivative / Code Berechnung der Ableitung](https://github.com/home-assistant/core/blob/7ed9967245957cd1b676a2f4dba853cc362a044f/homeassistant/components/derivative/sensor.py#L211)
   2. `<Differenz Sensortwert alt - Sensorwert neu> / <Sekunden zwischen beiden Sensorwerten> / 1 * <Sekunden = 60>`
   3. Einrichten als Helper `derivative_modulation`
2. Helper einrichten Schwellenwertsensor für `derivative_modulation`
   1. Hysterese: 0
   2. Untere Grenze: 0
   3. Obere Grenze: 1000
   4. Ergebnis: True/False für den Zeitraum, wenn der Wert positiv ist
   5. Muss der Schwellenwertsensor evtl. vor den Ableitungssensor? (non_negative_derivative)
3. Formel Pelletsverbrauch:
   1. `Schwellwert / 60 * <kW Leitung Pelletsheizung, z.B. 7.8kW> * `