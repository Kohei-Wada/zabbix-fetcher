import os
import time
import requests
from pyzabbix import ZabbixAPI


class Config:
    """Configuration loaded from environment variables."""
    def __init__(self):
        self.zabbix_url = os.getenv("ZABBIX_URL")
        self.zabbix_user = os.getenv("ZABBIX_USER")
        self.zabbix_pass = os.getenv("ZABBIX_PASS")
        self.api_endpoint = os.getenv("API_ENDPOINT", "http://localhost:8000")
        self.group_filter = [
            g.strip()
            for g in os.getenv("ZABBIX_GROUPS", "").split(",")
            if g.strip()
        ]
        self.ignore_hosts = [
            h.strip()
            for h in os.getenv("IGNORE_HOSTS", "").split(",")
            if h.strip()
        ]
        self.fetch_interval = int(os.getenv("FETCH_INTERVAL", 3600))


class ZabbixClient:
    """Wrapper around pyzabbix.ZabbixAPI for fetching groups, hosts, and proxies."""
    def __init__(self, config: Config, zapi=None):
        self.config = config
        if zapi is None:
            self.zapi = ZabbixAPI(self.config.zabbix_url)
            self.zapi.login(self.config.zabbix_user, self.config.zabbix_pass)
        else:
            self.zapi = zapi

    def get_group_ids(self):
        if not self.config.group_filter:
            return []
        all_groups = self.zapi.hostgroup.get(output=["groupid", "name"])
        group_map = {g["name"]: g["groupid"] for g in all_groups}
        return [group_map[g] for g in self.config.group_filter if g in group_map]

    def get_hosts(self, group_ids):
        host_filter = {"groupids": group_ids} if group_ids else {}
        return self.zapi.host.get(
            output=["hostid", "host", "name", "proxy_hostid"],
            selectInterfaces=["interfaceid", "ip", "port"],
            **host_filter
        )

    def get_proxy_map(self):
        proxies = self.zapi.proxy.get(output=["proxyid", "host"])
        return {p["proxyid"]: p["host"] for p in proxies}


class HostSyncer:
    """Builds payloads from Zabbix host data and sends them to an API endpoint."""
    def __init__(self, config: Config):
        self.config = config

    def build_payload(self, hosts, proxy_map):
        payload = []
        for h in hosts:
            if h.get("name") in self.config.ignore_hosts:
                continue
            interfaces = h.get("interfaces") or []
            if not interfaces:
                continue
            ip = interfaces[0].get("ip")
            port = interfaces[0].get("port")
            proxy_id = h.get("proxy_hostid")
            proxy_name = proxy_map.get(proxy_id)
            if not ip or not port:
                continue
            payload.append({
                "zabbix_url": self.config.zabbix_url,
                "hostid": h.get("hostid"),
                "host": h.get("host"),
                "name": h.get("name"),
                "ip": ip,
                "maintenance_port": port,
                "proxy_name": proxy_name
            })
        return payload

    def send(self, payload):
        if not payload:
            return None
        response = requests.post(self.config.api_endpoint, json=payload)
        return response