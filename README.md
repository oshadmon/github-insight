# github-insight

The following repository is intended to generate tables with traffic related insight from GitHub. 
Due to the limitation that GitHub doesn't provide IP addresses the daily result (ie `today`) is unique counts for that day. 

# Files & Sample code

```create_table.sql``` - SQL file containing  CREATE table statements for github specific tables 

```auth_pair.txt``` - Text file containing information that helps connect to a given GitHub repo & retrieve information  
 
```generate_github_data.py``` - Connect to Github, and retrieve insight regarding traffic, commit counts, clones count, and information regarding where visitors are coming from. 

```
ubuntu@ori-foglamp:~/github-insight$ python3 generate_github_data.py --help 
usage: generate_github_data.py [-h] [-d DIR] auth_file

positional arguments:
  auth_file          authentication file

optional arguments:
  -h, --help         show this help message and exit
  -d DIR, --dir DIR  directory to send data into (for JSON)

ubuntu@ori-foglamp:~/github-insight$ python3 generate_github_data.py $HOME/auth_pair.txt -d /tmp
ubuntu@ori-foglamp:~/github-insight$ cat sample.json 
{"timestamp": "2018-09-05 00:00:00", "key": "7d99dfeb-3b08-4cdc-b7f7-8fd345e954a4", "asset": "github/github-insight/traffic", "readings": {"count": 15}}
{"timestamp": "2018-09-05", "key": "c5bd8a5c-d64d-47cb-80d5-11f919335e60", "asset": "github/github-insight/commits", "readings": {"count": 19}}
{"timestamp": "2018-09-05T00:00:00Z", "key": "c8573a95-bff4-4db0-b1f6-f586f5796349", "asset": "github/github-insight/clones", "readings": {"count": 5}}
{"timestamp": "2018-09-05", "key": "97ca2db8-9793-4453-a054-ace5c8f69798", "asset": "github/github-insight/referrerals/github.com", "readings": {"count": 32}}
{"timestamp": "2018-09-05", "key": "c463483b-3aff-4473-b01d-e870b6bb899a", "asset": "github/github-insight/referrerals/Google", "readings": {"count": 18}}
{"timestamp": "2018-09-05", "key": "5ca3eb45-7fc0-479e-bcb5-9658e922340f", "asset": "github/github-insight/referrerals/DuckDuckGo", "readings": {"count": 1}}
{"timestamp": "2018-09-05", "key": "62e1c1ec-35c2-409a-b169-e22e840bcda9", "asset": "github/github-insight/referrerals/Bing", "readings": {"count": 1}}
...
```

```send_data.py``` - Given output file (generated by ```generate_github_data.py```) store results in corresponding tables in database. 

```
ubuntu@ori-foglamp:~/github-insight$ python3 send_data.py --help
usage: send_data.py [-h] [-up UP] [-hp HP] [-db DB] [-create CREATE] file_name

positional arguments:
  file_name             file with data from github

optional arguments:
  -h, --help            show this help message and exit
  -up UP, --up UP       user & password for database
  -hp HP, --hp HP       host & port for database
  -db DB, --db DB       database name for database
  -create CREATE, --create CREATE
                        SQL file with create tables
ubuntu@ori-foglamp:~/github-insight$ python3 send_data.py sample.json -up ubuntu:foglamp -hp 127.0.0.1:5432 -db github
```

# Notes 

Please use [Graphing](https://github.com/oshadmon/Graphing) to graph the data in the different tables. 
