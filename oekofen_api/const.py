"""
Constants
"""
from __future__ import annotations
from collections import OrderedDict

ATTR_TYPE_DICT = 'key-value-pair'
ATTR_TYPE_DESCRIPTION = 'description-text'
BASE_URL_TMPL = 'http://{host}:{port}/{json_password}/'
URL_PATH_ALL_WITH_FORMATS = 'all??'
RE_FIND_NUMBERS = r'\d+'
DEFAULT_PORT = 4321
UPDATE_INTERVAL_SECONDS = 10


# JSON Keys
JSON_KEY_FORMAT = 'format'
JSON_KEY_VALUE = 'val'
JSON_KEY_UNIT_OF_MEASUREMENT = 'unit'
JSON_KEY_FACTOR = 'factor'
JSON_KEY_MINIMUM = 'min'
JSON_KEY_MAXIMUM = 'max'
JSON_KEY_LENGTH = 'length'
JSON_KEY_READONLY_ATTRIBUTE_PREFIX = 'L_'


def format2dict(value: str) -> dict:
    d = OrderedDict()
    for sec in value.split('|'):
        key, text = sec.split(':')
        d[int(key)] = text
    return d


# conversion
IS_TEMP_ATTR = [
    'L_ambient',
    'L_temp',
    'L_flowtemp_act',
    'L_tpo_act',
    'L_tpm_act',
    'L_ontemp_act',
    'L_offtemp_act',
    'L_temp_act',
    'L_ret_temp',
    'L_release_temp',
]

IS_BOOL_ATTR = [
    'L_pump',
    'L_pummp'  # circ1
]

ON_VALUE = 'on'
OFF_VALUE = 'off'

# generic
OFF_ON_TEXT = "0:Aus|1:Ein"
GENERIC_OFF_ON_TEXT = format2dict(OFF_ON_TEXT)
SYSTEM_USB_STICK_TEXT = GENERIC_OFF_ON_TEXT
WEATHER_OEKOMODE_TEXT = GENERIC_OFF_ON_TEXT
HK_PUMP_TEXT = GENERIC_OFF_ON_TEXT
WW_PUMP_TEXT = GENERIC_OFF_ON_TEXT
WW_HEAT_ONCE_TEXT = GENERIC_OFF_ON_TEXT
WW_USE_BOILER_HEAT_TEXT = GENERIC_OFF_ON_TEXT
CIRC_PUMMP_TEXT = GENERIC_OFF_ON_TEXT  # why 2 MM in PUMP?
PE_BR = GENERIC_OFF_ON_TEXT     # L_br
PE_AK = GENERIC_OFF_ON_TEXT     # L_ak
PE_NOT = GENERIC_OFF_ON_TEXT    # L_not
PE_STB = GENERIC_OFF_ON_TEXT    # L_stb


ATTR_STATETEXT = 'L_statetext'

# "pe": pellematic data
# From http://<ip>:<port>/<json_password>/all? / pe1 / L_state / format
_PE_L_STATES = "0:Dauerlauf|1:Start|2:Zuendung|3:Softstart|4:Leistungsbrand|5:Nachlauf|6:Aus|7:Saugen|8:! Asche !|9:! Pellets !|" \
               "10:Pell Switch|11:Störung|12:Einmessen|13:1|14:1|15:1|16:1|17:1|18:1|19:1|20:1|21:1|22:1|23:1|24:1|25:1|26:1|27:1|" \
               "28:1|29:1|30:1|31:1|32:1|33:1|34:1|35:1|36:1|37:1|38:1|39:1|40:1|41:1|42:1|43:1|44:1|45:1|46:1|47:1|48:1|49:1|" \
               "50:1|51:1|52:1|53:1|54:1|55:1|56:1|57:1|58:1|59:1|60:1|61:1|62:1|63:1|64:1|65:1|66:1|67:1|68:1|69:1|" \
               "70:1|71:1|72:1|73:1|74:1|75:1|76:1|77:1|78:1|79:1|80:1|81:1|82:1|83:1|84:1|85:1|86:1|87:1|88:1|89:1|" \
               "90:1|91:1|92:1|93:1|94:1|95:1|96:1|97:Aus|98:Aus|99:Aus|100:Aus|101:Aus"
# From http://<ip>:<port>/<json_password>/all? / pe1 / L_type / format
_PE_L_TYPES = "0:PE|1:PES|2:PEK|3:PESK|4:SMART V1|5:SMART V2|6:CONDENS|7:SMART XS|8:SMART V3|9:COMPACT|10:AIR"

PE_STATES_TEXT = format2dict(_PE_L_STATES)
PE_TYPES_TEXT = format2dict(_PE_L_TYPES)

PE_STATE_START = 1
PE_STATE_FIRING = 2
PE_STATE_SOFTSTART = 3
PE_STATE_PERFORMANCE_FIRE = 4
PE_STATE_TRAILING = 5
PE_STATES_OFF = [6, 97, 98, 99, 100, 101]
PE_STATES_ERROR = [8, 9, 11]

# Pump
PUMP_STATE_OFF = 0
PUMP_STATE_ON = 1

# "ww": domestic hot water data
VERSION_SEPERATOR = '   '
