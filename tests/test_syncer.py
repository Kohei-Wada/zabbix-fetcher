import unittest

import requests
from unittest.mock import patch

from zabbix_fetcher import Config, HostSyncer


class TestHostSyncer(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.config.zabbix_url = "http://zabbix"
        self.config.ignore_hosts = ["n2"]
        self.config.api_endpoint = "http://api"
        self.syncer = HostSyncer(self.config)

    def test_build_payload(self):
        hosts = [
            {
                "hostid": "h1",
                "host": "host1",
                "name": "n1",
                "proxy_hostid": None,
                "interfaces": [{"ip": "1.1.1.1", "port": "1000"}],
            },
            {
                "hostid": "h2",
                "host": "host2",
                "name": "n2",
                "proxy_hostid": "p",
                "interfaces": [{"ip": "2.2.2.2", "port": "2000"}],
            },
            {
                "hostid": "h3",
                "host": "host3",
                "name": "n3",
                "proxy_hostid": "p",
                "interfaces": [],
            },
            {
                "hostid": "h4",
                "host": "host4",
                "name": "n4",
                "proxy_hostid": "p",
                "interfaces": [{"ip": None, "port": "3000"}],
            },
        ]
        proxy_map = {"p": "proxyhost"}
        payload = self.syncer.build_payload(hosts, proxy_map)
        self.assertEqual(len(payload), 1)
        expected = {
            "zabbix_url": "http://zabbix",
            "hostid": "h1",
            "host": "host1",
            "name": "n1",
            "ip": "1.1.1.1",
            "maintenance_port": "1000",
            "proxy_name": None,
        }
        self.assertEqual(payload[0], expected)

    @patch("zabbix_fetcher.requests.post")
    def test_send(self, mock_post):
        response = requests.Response()
        response.status_code = 200
        response._content = b"OK"
        mock_post.return_value = response

        data = [{"a": 1}]
        res = self.syncer.send(data)
        mock_post.assert_called_once_with("http://api", json=data)
        self.assertEqual(res, response)

    def test_send_empty(self):
        res = self.syncer.send([])
        self.assertIsNone(res)
