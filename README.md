 # zabbix-fetcher

 A script to fetch hosts from Zabbix and sync them to an API endpoint.

 ## Usage

 Set the required environment variables and run the main script:

 ```
 export ZABBIX_URL=http://your-zabbix-server
 export ZABBIX_USER=username
 export ZABBIX_PASS=password
 export API_ENDPOINT=http://your-api-endpoint
 export ZABBIX_GROUPS="group1,group2"      # optional
 export IGNORE_HOSTS="host1,host2"         # optional
 export FETCH_INTERVAL=3600                 # optional, default 3600 seconds

 python main.py
 ```

 ## Testing

 Run unit tests using Python's built-in unittest framework:

 ```
 python -m unittest discover
 ```
