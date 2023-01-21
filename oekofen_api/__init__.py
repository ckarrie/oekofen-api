from __future__ import annotations

from collections import OrderedDict
import logging
import aiohttp
import re
from datetime import datetime

from voluptuous import Optional
from . import const

logger = logging.getLogger(__name__)


class Oekofen(object):
    def __init__(self, host: str, json_password: str, port: int = const.DEFAULT_PORT, update_interval: int = const.UPDATE_INTERVAL_SECONDS):
        self.host = host
        self.update_interval = update_interval
        self._data = {}
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
            self._data = await self._fetch_data(path=const.URL_PATH_ALL_WITH_FORMATS)
            self._last_fetch = datetime.now()

            # Domain part
            for domain_with_index, attributes_dict in self._data.items():
                index_nrs = re.findall(const.RE_FIND_NUMBERS, domain_with_index)
                if index_nrs:
                    index_nr = index_nrs[0]
                else:
                    index_nr = 0
                domain_name = domain_with_index.replace(str(index_nr), '')
                domain = Domain(oekofen=self, name=domain_name, index=index_nr)
                if domain_name in self.domains:
                    self.domains[domain_name].append(domain)
                else:
                    self.domains[domain_name] = [domain]

                # Attribute part
                domain.update_attributes(data=attributes_dict)

        return self._data

    async def _fetch_data(self, path) -> Optional(dict):
        raw_url = f'{self.base_url}{path}'
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                resp = await session.get(raw_url)
                if resp.status == 200:
                    # no content type send from host, accepting all
                    json_response = await resp.json(content_type=None)
                    if json_response is not None:
                        return json_response
                    else:
                        return None

            except Exception as e:
                logger.error(e)
                raise

    def _has_valid_data(self):
        data_is_old = (datetime.now() - self._last_fetch).total_seconds() >= self.update_interval
        if (not self._data) or data_is_old:
            return False
        return True

    async def get_status(self):
        self._status = await self._get_value("pe", "L_statetext")
        return self._status

    async def get_weather_temp(self):
        v = await self._get_value('weather', 'L_temp')
        return v

    async def _get_value(self, domain: str, attribute: str, domain_index: int = 1):
        if not self._has_valid_data():
            await self.update_data()

        if domain_index < 1:
            return None
        domains = self.domains.get(domain, [])
        if len(domains) > (domain_index - 1):
            domain_instance = domains[domain_index - 1]
            attribute_instance = domain_instance.attributes.get(attribute, None)
            if attribute_instance is not None:
                return attribute_instance.get_value()
        return None

    def _set_value(self, domain_attribute: str, value: str):
        """

        :param domain_attribute: i.e. "hk1.mode_auto"
        :param value: "0"
        :return:
        """
        url = self.base_url + '{domain_attribute}={value}'.format(domain_attribute=domain_attribute, value=value)


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


class ControllableAttribute(Attribute):
    def set(self, value, value_is_normalized=False):
        if self.factor and not value_is_normalized:
            value = value * self.factor
        if self.min < value < self.max:
            print("Okay setting value %s" % value)
        else:
            print("Not Okay setting value %s" % value)


class MyOekofen(object):
    def __init__(self):
        pass
