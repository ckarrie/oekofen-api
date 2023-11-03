"""Oekofen API by Christian Karrié"""

from __future__ import annotations

from collections import OrderedDict
import logging
import re
import json
import time
from datetime import datetime
from voluptuous import Optional
from yarl import URL
import urllib.request
import urllib.error

from . import const

_LOGGER = logging.getLogger(__name__)

class Oekofen(object):
    def __init__(
        self,
        host: str,
        json_password: str,
        port: int = const.DEFAULT_PORT,
        update_interval: int = const.UPDATE_INTERVAL_SECONDS,
    ):
        self.host = host
        self.update_interval = update_interval
        self._raw_data = {}
        self._csv_data = OrderedDict()
        self.data = {}
        self._last_fetch = datetime.now()
        self._status = None
        self.domains = OrderedDict()
        self.base_url = const.BASE_URL_TMPL.format(
            host=host, port=port, json_password=json_password
        )

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.host})"

    def update_data(self):
        """
        - fetches the raw json from oekofen
        - flatten the received data to self.data

              "hk1.hk_info":"heating circuit data",
              "hk1.L_roomtemp_act":0.0,
              "hk1.L_roomtemp_act_min":-3276.8,
              "hk1.L_roomtemp_act_max":3276.7,

              dict-key = "<domain><domain_index>.<attribute>"
        """
        if not self._has_valid_data():
            self._raw_data = self._fetch_data(
                path=const.URL_PATH_ALL_WITH_FORMATS, is_json=True
            )
            self._last_fetch = datetime.now()
            self.domains = OrderedDict()

            metadata = {
                'ip_host': self.host,
                'installateur_code': self.get_installateur_code()
            }

            self.data = {
                "system_indexes": [""],  # empty domain
                "weather_indexes": [""],  # empty domain
                "forecast_indexes": [""],  # empty domain
                "error_indexes": [""],  # empty domain
                "meta_indexes": [""],  # empty domain, injected
                "hk_indexes": [],
                "pu_indexes": [],
                "ww_indexes": [],
                "circ_indexes": [],
                "pe_indexes": [],
                "sk_indexes": [],
            }

            _LOGGER.debug("[oekfoen_api.update_data] init_data=%s", self.data)

            # Domain part
            for domain_with_index, attributes_dict in self._raw_data.items():
                index_nrs = re.findall(const.RE_FIND_NUMBERS, domain_with_index)
                if index_nrs:
                    index_nr = int(index_nrs[0])
                else:
                    index_nr = None
                domain_name = domain_with_index.replace(str(index_nr), "")
                domain = Domain(oekofen=self, name=domain_name, index=index_nr)
                if domain_name in self.domains:
                    self.domains[domain_name].append(domain)
                else:
                    self.domains[domain_name] = [domain]

                if index_nr is not None:
                    self.data.setdefault(f"{domain_name}_indexes", [])
                    self.data[f"{domain_name}_indexes"].append(index_nr)

                # Attribute part
                domain.update_attributes(data=attributes_dict)

                # data-Part
                for att_key, att_value in attributes_dict.items():
                    if index_nr is None:
                        index_nr = 1
                    att_rendered_value = self._get_value(
                        domain=domain_name, attribute=att_key, domain_index=index_nr
                    )
                    self.data[f"{domain_with_index}.{att_key}"] = att_rendered_value
                    # special
                    att_instance = self.get_attribute(domain_name, att_key, index_nr)
                    if att_instance.choices is not None:
                        self.data[
                            f"{domain_with_index}.{att_key}_choice"
                        ] = att_instance.get_choice()
                    if att_instance.min is not None:
                        self.data[
                            f"{domain_with_index}.{att_key}_min"
                        ] = att_instance.get_min_value()
                    if att_instance.max is not None:
                        self.data[
                            f"{domain_with_index}.{att_key}_max"
                        ] = att_instance.get_max_value()

            # injecting metadata Part
            for k, v in metadata.items():
                self.data[f'meta.{k}'] = v

            if isinstance(self.data, dict) and "system.system_info" in self.data:
                #_LOGGER.debug("update_data=%s", self.data)
                return self.data

    def get_version(self):
        text_data = self._fetch_data("??", is_json=False, is_text=True)
        first_line = text_data.split("\n")[0].split(const.VERSION_SEPERATOR)
        # "['Oekofen JSON Interface', 'V4.00b', 'http://www.oekofen.at']"
        if len(first_line) == 3:
            return first_line[1]

    def update_csv_data(self):
        # URL http://192.168.178.222:4321/eMlG/log
        self._csv_data = OrderedDict()
        csv_data = self._fetch_data("log", is_json=False, is_text=True)
        csv_lines = csv_data.split("\r\n")
        cnt_csv_lines = len(csv_lines)
        first_line_splitted = csv_lines[0].split(";")
        last_line_splitted = csv_lines[cnt_csv_lines - 2].split(";")

        dt_day = datetime.now().replace(microsecond=0)

        _LOGGER.info("[Oekofen.update_csv_data] len(first_line_splitted)=%d", len(first_line_splitted))
        _LOGGER.info("[Oekofen.update_csv_data] len(last_line_splitted)=%d", len(last_line_splitted))

        for col, content in enumerate(first_line_splitted):
            content = content.replace("[»C]", "[°C]")
            raw_value = last_line_splitted[col]
            _LOGGER.debug("- %s %s %s", col, content, raw_value)
            if "," in raw_value:
                value = float(raw_value.replace(",", "."))
            elif "." in raw_value and len(raw_value.split(".")) == 3:
                day = int(raw_value.split(".")[0])
                month = int(raw_value.split(".")[1])
                year = int(raw_value.split(".")[2])
                dt_day = dt_day.replace(year=year, month=month, day=day)
                value = dt_day.date()
            elif ":" in raw_value and len(raw_value.split(":")) == 3:
                t_hour = int(raw_value.split(":")[0])
                t_min = int(raw_value.split(":")[1])
                t_sec = int(raw_value.split(":")[2])
                dt_day = dt_day.replace(hour=t_hour, minute=t_min, second=t_sec)
                value = dt_day.time()
                self._csv_data["timestamp"] = dt_day
            elif raw_value.isdigit():
                value = int(raw_value)
            else:
                value = raw_value

            content = content.rstrip()
            if len(content):
                self._csv_data[content] = value
        return self._csv_data

    def _fetch_data(
        self, path, is_json=True, is_text=False, retry=True
    ) -> Optional(dict):
        raw_url = f"{self.base_url}{path}"
        _LOGGER.info("[Oekofen._fetch_data] using urllib.request.urlopen url=%s", raw_url)
        try:
            resp = urllib.request.urlopen(raw_url)
            raw_data = resp.read()
            encoding = resp.info().get_content_charset(const.CHARSET)
            if resp.status == 200:
                if is_json:
                    json_data = json.loads(raw_data.decode(encoding))
                    if json_data is not None:
                        return json_data
                    return None
                if is_text:
                    return raw_data.decode(const.CHARSET)
                return True
        except urllib.error.HTTPError:
            if retry:
                time.sleep(2.5)
                data = self._fetch_data(
                    path=path, is_json=is_json, is_text=is_text, retry=False
                )
                return data
            else:
                raise
        except Exception as e:
            _LOGGER.error(e)
            raise

    def _has_valid_data(self):
        data_is_old = (
            datetime.now() - self._last_fetch
        ).total_seconds() >= self.update_interval
        if (not self._raw_data) or data_is_old:
            return False
        return True

    def _get_value(
        self, domain: str, attribute: str, domain_index: int = 1, return_attribute=False
    ):
        if domain_index < 1:
            return None
        if not self.domains:
            return None
        domains = self.domains.get(domain, [])
        if len(domains) > (domain_index - 1):
            domain_instance = domains[domain_index - 1]
            attribute_instance = domain_instance.attributes.get(attribute, None)
            if attribute_instance is not None:
                if return_attribute:
                    return attribute_instance
                return attribute_instance.get_value()
        return None

    def get_attribute(
        self, domain: str, attribute: str, domain_index: int = 1
    ) -> Attribute:
        return self._get_value(
            domain=domain,
            attribute=attribute,
            domain_index=domain_index,
            return_attribute=True,
        )

    def _send_set_value(self, domain_attribute: str, value: str):
        """

        :param domain_attribute: i.e. "hk1.mode_auto"
        :param value: "0"
        :return:
        """
        path = URL().with_name(f"{domain_attribute}={value}")
        self._fetch_data(path=str(path), is_json=False)

    def set_attribute_value(self, att: Attribute, value):
        if not isinstance(att, ControllableAttribute):
            return False
        val = att.generate_new_value(value=value, value_in_human_format=True)
        if att.domain.index is None:
            dom_att = f"{att.domain.name}.{att.key}"
        else:
            dom_att = f"{att.domain.name}{att.domain.index}.{att.key}"

        self._send_set_value(domain_attribute=dom_att, value=val)
        return value

    # Popular queries
    def get_name(self):
        return f"Oekofen ({self.host})"

    def get_status(self):
        self._status = self._get_value("pe", "L_statetext")
        return self._status

    def get_weather_temp(self):
        return self._get_value("weather", "L_temp")

    def get_heating_circuit_state(self) -> str:
        return self._get_value("hk", "L_statetext")

    def get_heating_circuit_temp(self) -> float:
        return self._get_value("hk", "temp_heat")

    def get_model(self) -> str:
        attr = self.get_attribute("pe", "L_type")
        return attr.get_choice()

    def get_uid(self):
        model = self.get_model().lower().replace(" ", "_")
        host = self.host.replace(".", "_")
        return f"oekofen_{model}_{host}"

    def set_heating_circuit_temp(self, celsius: float, domain_index: int = 1) -> bool:
        att = self.get_attribute("hk", "temp_heat", domain_index=domain_index)
        return self.set_attribute_value(att, celsius)

    @staticmethod
    def get_installateur_code():
        return datetime.now().strftime(const.INSTALLATEUR_CODE_FORMAT)


class Domain(object):
    def __init__(self, oekofen: Oekofen, name: str, index: int):
        self.name = name
        self.index = index
        self.oekofen = oekofen
        self.attributes = OrderedDict()

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.name}{self.index})"

    def update_attributes(self, data: dict):
        for k, v in data.items():
            if k.startswith(const.JSON_KEY_READONLY_ATTRIBUTE_PREFIX):
                att = Attribute(domain=self, key=k, data=v)
            else:
                att = ControllableAttribute(domain=self, key=k, data=v)
            self.attributes[k] = att


class Attribute(object):
    def __init__(self, domain: Domain, key: str, data: dict | str):
        self.key = key

        if isinstance(data, str):
            data = {const.JSON_KEY_VALUE: data}

        self.format: str | None = data.get(const.JSON_KEY_FORMAT, None)
        self.raw_value: str | float | int | None = data.get(const.JSON_KEY_VALUE, None)
        self.unit: str | None = data.get(const.JSON_KEY_UNIT_OF_MEASUREMENT, None)
        self.factor: float | int | None = data.get(const.JSON_KEY_FACTOR, None)
        self.min: float | int | None = data.get(const.JSON_KEY_MINIMUM, None)
        self.max: float | int | None = data.get(const.JSON_KEY_MAXIMUM, None)
        self.length: int | None = data.get(const.JSON_KEY_LENGTH, None)
        self.choices = None
        self.domain: Domain = domain
        if self.format:
            self.choices = const.format2dict(self.format)
        self.attributes = {}

        # fix '?C' unit:
        if isinstance(self.unit, str) and self.unit == "?C":
            self.unit = "°C"

        # convert numbers in strings to int/float
        if isinstance(self.factor, str):
            self.factor = float(self.factor)
            if self.factor == float(1):
                self.raw_value = int(self.raw_value)
            else:
                self.raw_value = float(self.raw_value)
            if self.min is not None:
                self.min = float(self.min)
            if self.max is not None:
                self.max = float(self.max)
        if isinstance(self.length, str):
            self.length = int(self.length)

        # keys with "format" can have non-int values as well
        if isinstance(self.format, str) and isinstance(self.raw_value, str):
            if self.raw_value == "false":
                self.raw_value = 0
            elif self.raw_value == "true":
                self.raw_value = 1
            else:
                self.raw_value = int(self.raw_value)

        # handle thirdparty (shelly) temp sensors
        if self.domain.name == 'thirdparty' and '|' in self.raw_value and self.key == 'L_state':
            p = self.raw_value.split('|')
            self.attributes = {
                'type_id': p[0],
                'device_id': p[1],
                'device_id_2': p[2],
                'temp_capable': p[3],
                'temperature': p[4],
                'humidity': p[5],
                'battery': p[6],
                'timestamp': p[7],
                'device_ip': p[8],
            }

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.key}={self.get_value_with_unit()})"

    def get_value(self, value=None):
        if not value:
            value = self.raw_value
        if value is not None:
            if self.factor is not None:
                # i.e. temperature or zs (zehntelsekunden, 0,1 seconds)
                v = float(value) * self.factor
                return float("{:.2f}".format(round(v, 2)))
            # handle thirdparty shelly temp sensors
            if self.domain.name == 'thirdparty' and '|' in self.raw_value and self.key == 'L_state':
                temp_sensor = float(int(self.raw_value.split('|')[4]) / 10)
                return temp_sensor
            if self.format == const.OFF_ON_TEXT:
                # bool on/off
                if value == 0:
                    return False
                else:
                    return True
        return value

    def get_value_with_unit(self) -> str:
        if self.unit:
            return f"{self.get_value()} {self.unit}"
        return self.get_value()

    def get_choice(self):
        if self.choices:
            return self.choices.get(self.raw_value)

    def get_min_value(self):
        if self.min is not None:
            return self.get_value(value=self.min)

    def get_max_value(self):
        if self.max is not None:
            return self.get_value(value=self.max)


class ControllableAttribute(Attribute):
    def generate_new_value(self, value, value_in_human_format=True):
        """

        :param value:
        :param value_in_human_format: True if temperature in `value` is in celsius and needs convertions 15 °C -> 150
        :return:
        """

        virtual_min = None
        virtual_max = None

        if self.choices:
            virtual_min = min(self.choices.keys())
            virtual_max = max(self.choices.keys())
        if self.min is not None and self.max is not None:
            virtual_min = self.min
            virtual_max = self.max

        if isinstance(self.raw_value, (float, int)) and isinstance(value, (float, int)):
            if self.factor and value_in_human_format:
                value = int(value / self.factor)

            if (
                virtual_min is not None
                and virtual_max is not None
                and virtual_min <= value <= virtual_max
            ):
                _LOGGER.info("[ControllableAttribute.generate_new_value] Okay setting value %s", value)
                return value
            else:
                raise ValueOutOfBoundaryError(
                    "setting value %s, min=%s, max=%s"
                    % (value, virtual_min, virtual_max)
                )

        if isinstance(self.raw_value, str) and isinstance(value, str):
            if self.length is not None:
                if len(value) > self.length:
                    value = value[: self.length]
                return value

        return value


class MyOekofen(object):
    def __init__(self):
        pass


class OekofenAPIException(Exception):
    pass


class ValueOutOfBoundaryError(OekofenAPIException):
    pass
