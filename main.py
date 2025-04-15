import os
import time
import requests
from pyzabbix import ZabbixAPI

ZABBIX_URL = os.getenv("ZABBIX_URL")
ZABBIX_USER = os.getenv("ZABBIX_USER")
ZABBIX_PASS = os.getenv("ZABBIX_PASS")
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000")

GROUP_FILTER = [g.strip() for g in os.getenv(
    "ZABBIX_GROUPS", "").split(",") if g.strip()]
IGNORE_HOSTS = [h.strip() for h in os.getenv(
    "IGNORE_HOSTS", "").split(",") if h.strip()]
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", 3600))


def fetch_and_send_hosts():
    try:
        zapi = ZabbixAPI(ZABBIX_URL)
        zapi.login(ZABBIX_USER, ZABBIX_PASS)
    except Exception as e:
        print(f"Error connecting to Zabbix API: {e}")
        return

    group_ids = []
    if GROUP_FILTER:
        try:
            all_groups = zapi.hostgroup.get(output=["groupid", "name"])
            group_map = {g["name"]: g["groupid"] for g in all_groups}
            group_ids = [group_map[g] for g in GROUP_FILTER if g in group_map]
        except Exception as e:
            print(f"Error fetching Zabbix groups: {e}")
            return

    host_filter = {"groupids": group_ids} if group_ids else {}

    try:
        hosts = zapi.host.get(
            output=["hostid", "host", "name", "proxy_hostid"],
            selectInterfaces=["interfaceid", "ip", "port"],
            **host_filter
        )
    except Exception as e:
        print(f"Error fetching Zabbix hosts: {e}")
        return

    try:
        proxies = zapi.proxy.get(output=["proxyid", "host"])
        proxy_map = {p["proxyid"]: p["host"] for p in proxies}
    except Exception as e:
        print(f"Error fetching Zabbix proxies: {e}")
        return

    payload = []

    for h in hosts:
        if h["name"] in IGNORE_HOSTS:
            continue

        ip = h["interfaces"][0]["ip"] if h["interfaces"] else None
        port = h["interfaces"][0]["port"] if h["interfaces"] else None
        proxy_id = h.get("proxy_hostid")
        proxy_name = proxy_map.get(proxy_id)

        if not ip or not port:
            continue

        payload.append({
            "zabbix_url": ZABBIX_URL,
            "hostid": h["hostid"],
            "host": h["host"],
            "name": h["name"],
            "ip": ip,
            "maintenance_port": port,
            "proxy_name": proxy_name
        })

    if not payload:
        print("No valid hosts to send.")
        return

    try:
        res = requests.post(API_ENDPOINT, json=payload)
        if res.status_code == 200:
            print(f"Successfully synced {len(payload)} hosts to API")
        else:
            print(f"API error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    while True:
        fetch_and_send_hosts()
        print(f"Sleeping for {FETCH_INTERVAL} seconds...")
        time.sleep(FETCH_INTERVAL)

