import os
import unittest

from zabbix_fetcher import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self._env_backup = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env_backup)

    def test_default_values(self):
        os.environ.pop("ZABBIX_URL", None)
        os.environ.pop("ZABBIX_USER", None)
        os.environ.pop("ZABBIX_PASS", None)
        os.environ.pop("ZABBIX_GROUPS", None)
        os.environ.pop("IGNORE_HOSTS", None)
        os.environ.pop("API_ENDPOINT", None)
        os.environ.pop("FETCH_INTERVAL", None)

        config = Config()
        self.assertIsNone(config.zabbix_url)
        self.assertIsNone(config.zabbix_user)
        self.assertIsNone(config.zabbix_pass)
        self.assertEqual(config.group_filter, [])
        self.assertEqual(config.ignore_hosts, [])
        self.assertEqual(config.api_endpoint, "http://localhost:8000")
        self.assertEqual(config.fetch_interval, 3600)

    def test_env_values(self):
        os.environ["ZABBIX_URL"] = "http://zabbix"
        os.environ["ZABBIX_USER"] = "user"
        os.environ["ZABBIX_PASS"] = "pass"
        os.environ["ZABBIX_GROUPS"] = "grp1, grp2"
        os.environ["IGNORE_HOSTS"] = "host1,host2"
        os.environ["API_ENDPOINT"] = "http://api"
        os.environ["FETCH_INTERVAL"] = "123"

        config = Config()
        self.assertEqual(config.zabbix_url, "http://zabbix")
        self.assertEqual(config.zabbix_user, "user")
        self.assertEqual(config.zabbix_pass, "pass")
        self.assertEqual(config.group_filter, ["grp1", "grp2"])
        self.assertEqual(config.ignore_hosts, ["host1", "host2"])
        self.assertEqual(config.api_endpoint, "http://api")
        self.assertEqual(config.fetch_interval, 123)