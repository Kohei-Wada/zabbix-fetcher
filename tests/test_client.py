import unittest

from zabbix_fetcher import Config, ZabbixClient


class DummyHostgroup:
    def __init__(self, data):
        self._data = data

    def get(self, output):
        return self._data


class DummyHost:
    def __init__(self, data):
        self._data = data

    def get(self, output, selectInterfaces=None, **kwargs):
        return self._data


class DummyProxy:
    def __init__(self, data):
        self._data = data

    def get(self, output):
        return self._data


class DummyZapi:
    def __init__(self, groups, hosts, proxies):
        self.hostgroup = DummyHostgroup(groups)
        self.host = DummyHost(hosts)
        self.proxy = DummyProxy(proxies)


class TestZabbixClient(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.config.group_filter = ["g1", "g2"]
        self.groups = [{"groupid": "1", "name": "g1"}, {"groupid": "2", "name": "x"}]
        self.hosts = [
            {
                "hostid": "h1",
                "host": "host1",
                "name": "n1",
                "proxy_hostid": "p1",
                "interfaces": [
                    {"interfaceid": "i1", "ip": "127.0.0.1", "port": "1000"}
                ],
            }
        ]
        self.proxies = [{"proxyid": "p1", "host": "proxyhost"}]
        dummy = DummyZapi(self.groups, self.hosts, self.proxies)
        self.client = ZabbixClient(self.config, zapi=dummy)

    def test_get_group_ids(self):
        ids = self.client.get_group_ids()
        self.assertEqual(ids, ["1"])

    def test_get_hosts(self):
        hosts = self.client.get_hosts(group_ids=["1"])
        self.assertEqual(hosts, self.hosts)

        hosts_no_filter = self.client.get_hosts(group_ids=[])
        self.assertEqual(hosts_no_filter, self.hosts)

    def test_get_proxy_map(self):
        proxy_map = self.client.get_proxy_map()
        self.assertEqual(proxy_map, {"p1": "proxyhost"})