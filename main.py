import time

from zabbix_fetcher import Config, ZabbixClient, HostSyncer


def main():
    config = Config()
    try:
        client = ZabbixClient(config)
    except Exception as e:
        print(f"Failed to initialize Zabbix client: {e}")
        return
    syncer = HostSyncer(config)

    while True:
        try:
            group_ids = client.get_group_ids()
            hosts = client.get_hosts(group_ids)
            proxy_map = client.get_proxy_map()
            payload = syncer.build_payload(hosts, proxy_map)

            if not payload:
                print("No valid hosts to send.")
            else:
                res = syncer.send(payload)
                if res and res.status_code == 200:
                    print(f"Successfully synced {len(payload)} hosts to API")
                else:
                    status = res.status_code if res else "N/A"
                    text = res.text if res else ""
                    print(f"API error: {status} - {text}")
        except Exception as e:
            print(f"Error during sync: {e}")

        print(f"Sleeping for {config.fetch_interval} seconds...")
        time.sleep(config.fetch_interval)


if __name__ == "__main__":
    main()

