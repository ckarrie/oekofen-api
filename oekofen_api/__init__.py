from __future__ import annotations

from collections import OrderedDict
import logging
import aiohttp
import re
from datetime import datetime

from voluptuous import Optional
from yarl import URL

from . import const

logger = logging.getLogger(__name__)


class Oekofen(object):
    def __init__(self, host: str, json_password: str, port: int = const.DEFAULT_PORT, update_interval: int = const.UPDATE_INTERVAL_SECONDS):
        self.host = host
        self.update_interval = update_interval
        self._raw_data = {}
        self.data = {}
        self._last_fetch = datetime.now()
        self._status = None
        self.domains = OrderedDict()
        self.base_url = const.BASE_URL_TMPL.format(
            host=host,
            port=port,
            json_password=json_password
        )

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.host})"

    async def update_data(self):
        if not self._has_valid_data():
            self._raw_data = await self._fetch_data(path=const.URL_PATH_ALL_WITH_FORMATS)
            self._last_fetch = datetime.now()
            self.domains = OrderedDict()

            self.data = {
                'hk_indexes': [],
                'pu_indexes': [],
                'ww_indexes': [],
                'circ_indexes': [],
                'pe_indexes': [],
            }

            # Domain part
            for domain_with_index, attributes_dict in self._raw_data.items():
                index_nrs = re.findall(const.RE_FIND_NUMBERS, domain_with_index)
                if index_nrs:
                    index_nr = int(index_nrs[0])
                else:
                    index_nr = None
                domain_name = domain_with_index.replace(str(index_nr), '')
                domain = Domain(oekofen=self, name=domain_name, index=index_nr)
                if domain_name in self.domains:
                    self.domains[domain_name].append(domain)
                else:
                    self.domains[domain_name] = [domain]

                if index_nr is not None:
                    self.data.setdefault(f'{domain_name}_indexes', [])
                    self.data[f'{domain_name}_indexes'].append(index_nr)

                # Attribute part
                domain.update_attributes(data=attributes_dict)

                # data-Part
                for att_key, att_value in attributes_dict.items():
                    if index_nr is None:
                        index_nr = 1
                    att_rendered_value = self._get_value(domain=domain_name, attribute=att_key, domain_index=index_nr)
                    self.data[f'{domain_with_index}.{att_key}'] = att_rendered_value

            if isinstance(self.data, dict) and 'system.system_info' in self.data:
                return self.data

    async def _fetch_data(self, path, is_json=True) -> Optional(dict):
        raw_url = f'{self.base_url}{path}'
        print("_fetch_data", raw_url)
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                resp = await session.get(raw_url)
                if resp.status == 200:
                    # no content type send from host, accepting all with content_type=None
                    if is_json:
                        json_response = await resp.json(content_type=None)
                        if json_response is not None:
                            return json_response
                        else:
                            return None
                    return True

            except Exception as e:
                logger.error(e)
                raise

    def _has_valid_data(self):
        data_is_old = (datetime.now() - self._last_fetch).total_seconds() >= self.update_interval
        if (not self._raw_data) or data_is_old:
            return False
        return True

    def _get_value(self, domain: str, attribute: str, domain_index: int = 1, return_attribute=False):
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

    def get_attribute(self, domain: str, attribute: str, domain_index: int = 1) -> Attribute:
        return self._get_value(domain=domain, attribute=attribute, domain_index=domain_index, return_attribute=True)

    async def _send_set_value(self, domain_attribute: str, value: str):
        """

        :param domain_attribute: i.e. "hk1.mode_auto"
        :param value: "0"
        :return:
        """
        path = URL().with_name(f'{domain_attribute}={value}')
        return await self._fetch_data(path=str(path), is_json=False)

    async def set_attribute_value(self, att: Attribute, value):
        if not isinstance(att, ControllableAttribute):
            return False
        val = att.generate_new_value(value=value, value_in_human_format=True)
        dom_att = f'{att.domain.name}{att.domain.index}.{att.key}'
        value_set = await self._send_set_value(domain_attribute=dom_att, value=val)
        return value_set

    # Popular queries
    def get_name(self):
        return f'Oekofen ({self.host})'

    def get_status(self):
        self._status = self._get_value("pe", "L_statetext")
        return self._status

    def get_weather_temp(self):
        return self._get_value('weather', 'L_temp')

    def get_heating_circuit_state(self) -> str:
        return self._get_value('hk', 'L_statetext')

    def get_heating_circuit_temp(self) -> float:
        return self._get_value('hk', 'temp_heat')

    def get_model(self) -> str:
        attr = self.get_attribute('pe', 'L_type')
        return attr.get_choice()

    def get_uid(self):
        model = self.get_model().lower().replace(' ', '_')
        host = self.host.replace('.', '_')
        return f'oekofen_{model}_{host}'

    async def set_heating_circuit_temp(self, celsius: float, domain_index: int = 1) -> bool:
        att = self.get_attribute('hk', 'temp_heat', domain_index=domain_index)
        return await self.set_attribute_value(att, celsius)


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
            data = {
                const.JSON_KEY_VALUE: data
            }

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

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.key}={self.get_value_with_unit()})"

    def get_value(self):
        if self.raw_value:
            if self.factor is not None:
                # i.e. temperature
                return self.raw_value * self.factor
            if self.format == const.OFF_ON_TEXT:
                # bool on/off
                if self.raw_value == 0:
                    return False
                else:
                    return True

        return self.raw_value

    def get_value_with_unit(self) -> str:
        if self.unit:
            return f'{self.get_value()} {self.unit}'
        return self.get_value()

    def get_choice(self):
        if self.choices:
            return self.choices.get(self.raw_value)


class ControllableAttribute(Attribute):
    def generate_new_value(self, value, value_in_human_format=True):
        """

        :param value:
        :param value_in_human_format: True if temperature in `value` is in celsius and needs convertions 15 °C -> 150
        :return:
        """
        if isinstance(self.raw_value, (float, int)) and isinstance(value, (float, int)):
            if self.factor and value_in_human_format:
                value = int(value / self.factor)
            if self.min < value < self.max:
                print("Okay setting value %s" % value)
                return value
            else:
                raise ValueOutOfBoundaryError("setting value %s, min=%s, max=%s" % (value, self.min, self.max))

        if isinstance(self.raw_value, str) and isinstance(value, str):
            if self.length is not None:
                if len(value) > self.length:
                    value = value[:self.length]
                return value

        return value


class MyOekofen(object):
    def __init__(self):
        pass


class OekofenAPIException(Exception):
    pass


class ValueOutOfBoundaryError(OekofenAPIException):
    pass


