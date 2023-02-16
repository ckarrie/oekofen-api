# Testserver

import json
import random
from flask import Flask, Response

# Content of 'PASS/all?'
dummy_data = {
   "system":{
      "system_info":"system global variables",
      "L_ambient":{"val":"-25", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_errors":{"val":"0", "factor":"1", "min":"-32768", "max":"32767"},
      "L_usb_stick":{"val":"false", "format":"0:Aus|1:Ein"}
   },
   "weather":{
      "weather_info":"current weather data",
      "L_temp":{"val":"-20", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_clouds":{"val":"20", "unit":"%", "factor":"1", "min":"-32768", "max":"32767"},
      "L_forecast_temp":{"val":"40", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_forecast_clouds":{"val":"44", "unit":"%", "factor":"1", "min":"-32768", "max":"32767"},
      "L_forecast_today":{"val":"false", "format":"0:Heute|1:Morgen"},
      "L_starttime":{"val":"920", "factor":"1", "min":"-32768", "max":"32767"},
      "L_endtime":{"val":"1530", "factor":"1", "min":"-32768", "max":"32767"},
      "L_source":{"val":"http://www.openweathermap.org", "length":"20"},
      "L_location":{"val":"Kropp|DE|6551974", "length":"20"},
      "cloud_limit":{"val":"55", "unit":"%", "factor":"1", "min":"0.0", "max":"100.0"},
      "hysteresys":{"val":"-40", "unit":"K", "factor":"0.1", "min":"-200.0", "max":"0.0"},
      "offtemp":{"val":"-100", "unit":"?C", "factor":"0.1", "min":"-300.0", "max":"200.0"},
      "lead":{"val":"120", "unit":"min", "factor":"1", "min":"0.0", "max":"600.0"},
      "refresh":{"val":"false"},
      "oekomode":{"val":"1", "format":"0:Aus|1:Ein"}
   },
   "forecast":{
      "forecast_info":"date|temp|cloud|speed|image|code|unit[|sunrise|sunset] code see https://openweathermap.org/weather-conditions",
      "L_w_0":{"val":"Di, 7 Feb 21:50|-2|20|9 km/h|02n|801|C|08:00|17:11", "length":"20"},
      "L_w_1":{"val":"Mi, 8 Feb 01:00|-2|27|9 km/h|03n|802|C", "length":"20"},
      "L_w_2":{"val":"Mi, 8 Feb 04:00|-1|73|9 km/h|04n|803|C", "length":"20"},
      "L_w_3":{"val":"Mi, 8 Feb 07:00|-1|70|10 km/h|04n|803|C", "length":"20"},
      "L_w_4":{"val":"Mi, 8 Feb 10:00|1|23|12 km/h|02d|801|C", "length":"20"},
      "L_w_5":{"val":"Mi, 8 Feb 13:00|5|33|16 km/h|03d|802|C", "length":"20"},
      "L_w_6":{"val":"Mi, 8 Feb 16:00|4|55|13 km/h|04d|803|C", "length":"20"},
      "L_w_7":{"val":"Mi, 8 Feb 19:00|0|59|14 km/h|04n|803|C", "length":"20"},
      "L_w_8":{"val":"Mi, 8 Feb 22:00|-1|62|16 km/h|04n|803|C", "length":"20"},
      "L_w_9":{"val":"Do, 9 Feb 01:00|-1|65|17 km/h|04n|803|C", "length":"20"},
      "L_w_10":{"val":"Do, 9 Feb 04:00|-1|97|19 km/h|04n|804|C", "length":"20"},
      "L_w_11":{"val":"Do, 9 Feb 07:00|0|99|20 km/h|04n|804|C", "length":"20"},
      "L_w_12":{"val":"Do, 9 Feb 10:00|1|100|21 km/h|04d|804|C", "length":"20"},
      "L_w_13":{"val":"Do, 9 Feb 13:00|3|100|24 km/h|04d|804|C", "length":"20"},
      "L_w_14":{"val":"Do, 9 Feb 16:00|4|99|17 km/h|04d|804|C", "length":"20"},
      "L_w_15":{"val":"Do, 9 Feb 19:00|1|99|15 km/h|04n|804|C", "length":"20"},
      "L_w_16":{"val":"Do, 9 Feb 22:00|3|100|21 km/h|04n|804|C", "length":"20"},
      "L_w_17":{"val":"Fr, 10 Feb 01:00|3|100|20 km/h|04n|804|C", "length":"20"},
      "L_w_18":{"val":"Fr, 10 Feb 04:00|3|100|14 km/h|10n|500|C", "length":"20"},
      "L_w_19":{"val":"Fr, 10 Feb 07:00|2|100|11 km/h|04n|804|C", "length":"20"},
      "L_w_20":{"val":"Fr, 10 Feb 10:00|5|100|16 km/h|04d|804|C", "length":"20"},
      "L_w_21":{"val":"Fr, 10 Feb 13:00|5|100|24 km/h|04d|804|C", "length":"20"},
      "L_w_22":{"val":"Fr, 10 Feb 16:00|5|100|30 km/h|04d|804|C", "length":"20"},
      "L_w_23":{"val":"Fr, 10 Feb 19:00|5|100|33 km/h|04n|804|C", "length":"20"},
      "L_w_24":{"val":"Fr, 10 Feb 22:00|5|100|34 km/h|10n|500|C", "length":"20"}
   },
   "hk1":{
      "hk_info":"heating circuit data",
      "L_roomtemp_act":{"val":"0", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_roomtemp_set":{"val":"250", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_flowtemp_act":{"val":"486", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_flowtemp_set":{"val":"475", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_comfort":{"val":"0", "unit":"K", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_state":{"val":"32", "factor":"1"},
      "L_statetext":"Heizbetrieb aktiv",
      "L_pump":{"val":"true", "format":"0:Aus|1:Ein"},
      "remote_override":{"val":"0", "unit":"K", "factor":"0.1", "min":"-32768", "max":"32767"},
      "mode_auto":{"val":"1", "format":"0:Aus|1:Auto|2:Heizen|3:Absenken"},
      "time_prg":{"val":"0", "format":"0:Zeit 1|1:Zeit 2"},
      "temp_setback":{"val":"138", "unit":"?C", "factor":"0.1", "min":"100.0", "max":"400.0"},
      "temp_heat":{"val":"250", "unit":"?C", "factor":"0.1", "min":"100.0", "max":"400.0"},
      "temp_vacation":{"val":"150", "unit":"?C", "factor":"0.1", "min":"100.0", "max":"400.0"},
      "name":{"val":"", "length":"20"},
      "oekomode":{"val":"3", "format":"0:Aus|1:Komfort|2:Minimum|3:?kologisch"},
      "autocomfort":{"val":"-1", "format":"0:Aus|1:Ein|2:Morgens|3:Abends"},
      "autocomfort_sunset":{"val":"0", "unit":"min", "factor":"1", "min":"-120.0", "max":"120.0"},
      "autocomfort_sunrise":{"val":"0", "unit":"min", "factor":"1", "min":"-120.0", "max":"120.0"}
   },
   "pu1":{
      "pu_info":"accu data",
      "L_tpo_act":{"val":"564", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_tpo_set":{"val":"525", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_tpm_act":{"val":"395", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_tpm_set":{"val":"525", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_pump_release":{"val":"620", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_pump":{"val":"45", "unit":"%", "factor":"1", "min":"0.0", "max":"100.0"},
      "L_state":{"val":"256", "factor":"1"},
      "L_statetext":"Anforderung Ein",
      "mintemp_off":{"val":"80", "unit":"?C", "factor":"0.1", "min":"80.0", "max":"900.0"},
      "mintemp_on":{"val":"80", "unit":"?C", "factor":"0.1", "min":"80.0", "max":"900.0"},
      "ext_mintemp_off":{"val":"80", "unit":"?C", "factor":"0.1", "min":"80.0", "max":"900.0"},
      "ext_mintemp_on":{"val":"80", "unit":"?C", "factor":"0.1", "min":"80.0", "max":"900.0"}
   },
   "ww1":{
      "ww_info":"domestic hot water data",
      "L_temp_set":{"val":"250", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_ontemp_act":{"val":"559", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_offtemp_act":{"val":"559", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_pump":{"val":"false", "format":"0:Aus|1:Ein"},
      "L_state":{"val":"8200", "factor":"1"},
      "L_statetext":"Zeit au?erhalb Zeitprogramm|Anforderung Aus",
      "time_prg":{"val":"1", "format":"0:Zeit 1|1:Zeit 2"},
      "sensor_on":{"val":"0", "format":"0:WW|1:TPO|2:TPM|3:SpUnten"},
      "sensor_off":{"val":"0", "format":"0:WW|1:TPO|2:TPM|3:SpUnten"},
      "mode_auto":{"val":"1", "format":"0:Aus|1:Auto|2:Ein"},
      "mode_dhw":{"val":"1", "format":"0:Aus|1:Auto|2:Ein"},
      "heat_once":{"val":"false", "format":"0:Aus|1:Ein"},
      "temp_min_set":{"val":"300", "unit":"?C", "factor":"0.1", "min":"80.0", "max":"800.0"},
      "temp_max_set":{"val":"600", "unit":"?C", "factor":"0.1", "min":"80.0", "max":"800.0"},
      "name":{"val":"", "length":"20"},
      "smartstart":{"val":"0", "unit":"min", "factor":"1", "min":"0.0", "max":"90.0"},
      "use_boiler_heat":{"val":"0", "format":"0:Aus|1:Ein"},
      "oekomode":{"val":"3", "format":"0:Aus|1:Komfort|2:Minimum|3:?kologisch"}
   },
   "sk1":{
      "sk_info":"solar circuit data",
      "L_koll_temp":{"val":"-41", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_spu":{"val":"387", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_pump":{"val":"0", "unit":"%", "factor":"1", "min":"0.0", "max":"100.0"},
      "L_state":{"val":"32", "factor":"1"},
      "L_statetext":"Differenz Kollektor-Speicher zu niedrig",
      "mode":{"val":"1", "format":"0:Aus|1:Ein"},
      "cooling":{"val":"1", "format":"0:Aus|1:?kologisch|2:Ein"},
      "spu_max":{"val":"750", "unit":"?C", "factor":"0.1", "min":"200.0", "max":"900.0"},
      "name":{"val":"", "length":"20"}
   },
   "pe1":{
      "pe_info":"pellematic data",
      "L_temp_act":{"val":"631", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_temp_set":{"val":"760", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_ext_temp":{"val":"-32768", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_frt_temp_act":{"val":"7785", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_frt_temp_set":{"val":"6927", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_br":{"val":"false", "format":"0:Aus|1:Ein"},
      "L_ak":{"val":"false", "format":"0:Aus|1:Ein"},
      "L_not":{"val":"true", "format":"0:Aus|1:Ein"},
      "L_stb":{"val":"true", "format":"0:Aus|1:Ein"},
      "L_modulation":{"val":"100", "unit":"%", "factor":"1", "min":"-32768", "max":"32767"},
      "L_uw_speed":{"val":"45", "unit":"%", "factor":"1", "min":"-32768", "max":"32767"},
      "L_state":{"val":"4", "format":"0:Dauerlauf|1:Start|2:Zuendung|3:Softstart|4:Leistungsbrand|5:Nachlauf|6:Aus|7:Saugen|8:! Asche !|9:! Pellets !|10:Pell Switch|11:St?rung|12:Einmessen|13:1|14:1|15:1|16:1|17:1|18:1|19:1|20:1|21:1|22:1|23:1|24:1|25:1|26:1|27:1|28:1|29:1|30:1|31:1|32:1|33:1|34:1|35:1|36:1|37:1|38:1|39:1|40:1|41:1|42:1|43:1|44:1|45:1|46:1|47:1|48:1|49:1|50:1|51:1|52:1|53:1|54:1|55:1|56:1|57:1|58:1|59:1|60:1|61:1|62:1|63:1|64:1|65:1|66:1|67:1|68:1|69:1|70:1|71:1|72:1|73:1|74:1|75:1|76:1|77:1|78:1|79:1|80:1|81:1|82:1|83:1|84:1|85:1|86:1|87:1|88:1|89:1|90:1|91:1|92:1|93:1|94:1|95:1|96:1|97:Aus|98:Aus|99:Aus|100:Aus|101:Aus"},
      "L_statetext":"Leistungsbrand",
      "L_type":{"val":"0", "format":"0:PE|1:PES|2:PEK|3:PESK|4:SMART V1|5:SMART V2|6:CONDENS|7:SMART XS|8:SMART V3|9:COMPACT|10:AIR"},
      "L_starts":{"val":"14191", "factor":"1"},
      "L_runtime":{"val":"23306", "unit":"h", "factor":"1"},
      "L_avg_runtime":{"val":"98", "unit":"min", "factor":"1"},
      "L_uw_release":{"val":"620", "unit":"?C", "factor":"0.1", "min":"-32768", "max":"32767"},
      "L_uw":{"val":"45", "unit":"%", "factor":"1", "min":"-32768", "max":"32767"},
      "L_storage_fill":{"val":"20208", "unit":"kg", "factor":"1"},
      "L_storage_min":{"val":"400", "unit":"kg", "factor":"1", "min":"0.0", "max":"4000.0"},
      "L_storage_max":{"val":"6000", "unit":"kg", "factor":"1", "min":"150.0", "max":"30000.0"},
      "L_storage_popper":{"val":"0", "unit":"kg", "factor":"1", "min":"-32768", "max":"32767"},
      "storage_fill_today":{"val":"0", "unit":"kg", "factor":"1", "min":"-32768", "max":"32767"},
      "storage_fill_yesterday":{"val":"-20208", "unit":"kg", "factor":"1", "min":"-32768", "max":"32767"},
      "mode":{"val":"1", "format":"0:Aus|1:Auto|2:Ein"}
   },
   "error":{
   }
}

# First line of 'PASS/??'
dummy_error_text = "http://www.oekofen.at"


app = Flask(__name__)

@app.route('/')
def hello():
    return Response(response="Hello world", status=200, mimetype="") 

@app.route('/PASS/')
def error_text():
    return Response(response=dummy_error_text, status=200, mimetype="") 
   
@app.route('/PASS/all')
def oekofen_formatted_values():
    dummy_data["pe1"]["L_frt_temp_act"]["val"] = f'{random.randint(4000, 7000)}'
    dummy_data["pe1"]["L_temp_act"]["val"] = f'{random.randint(4000, 7000)}'
    return Response(response=json.dumps(dummy_data), status=200, mimetype="application/json")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4321)



