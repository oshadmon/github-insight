#!/bin/user/python
"""
Name: Ori Shadmon
Date: August 2018 
Description: The following code takes GitHub connection info, and generates traffic, commits, clones and referrals insigh. 
             The result is then saved into a JSON file.  
Notes: This process is based on code written by @nchah (https://github.com/nchah/github-traffic-stats)
""" 
import argparse
import datetime
import json
import os
import queue
import requests
import threading
import uuid


def get_timestamp(que:queue.Queue=None)->str:
   """
   Create a current timestamp
   """
   timestamp=datetime.datetime.now()
   que.put(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

def send_request(traffic_que:queue.Queue=None, commits_que:queue.Queue=None, clones_que:queue.Queue()=None,  
                 referrers_que:queue.Queue=None, repo:str='', organization:str='', auth_pair:tuple=())->(requests.models.Response, requests.models.Response, requests.models.Response, requests.models.Response): 
   """
   Send request to specific Github API endpoint
   :param:
      traffic_que:queue.Queue - que to store traffic results 
      commits_que:queue.Queue - que to store commits reults 
      clones_que:queue.Queue - que to store clones results 
      referrers_que:queue.Queue - que to store referrers result
      repo:str - repository name
      organization:str - organization name 
      auth_pair:tuple - user/password tuple pair
   :return: 
      request response for traffic, commits, and clones
   """

   # Traffic 
   base_url = 'https://api.github.com/repos/'
   traffic_url = base_url + organization + '/' + repo + '/traffic/views'
   traffic_response = requests.get(traffic_url, auth=auth_pair)

   if traffic_response.status_code != 200: 
      print("Error %s: %s " % (traffic_response.status_code, traffic_response.json()['message']))
      exit(1) 

   # Commits 
   commits_url = base_url + organization + '/' + repo + '/commits' 
   commits_response = requests.get(commits_url, auth=auth_pair)

   # Clones 
   base_url = 'https://api.github.com/repos/'
   base_url = base_url + organization + '/' + repo + '/traffic/clones'
   clones_response = requests.get(base_url, auth=auth_pair)

   # referrers 
   base_url = 'https://api.github.com/repos/'
   referrers_url = base_url + organization + '/' + repo + '/traffic/popular/referrers'
   referrers_response = requests.get(referrers_url, auth=auth_pair)

   traffic_que.put(traffic_response) 
   commits_que.put(commits_response)
   clones_que.put(clones_response)
   referrers_que.put(referrers_response)
  
def read_traffic(traffic:requests.models.Response=None, repo:str='repo_name')->list:
   """
   Create list of JSON objects with traffic info
   :param: 
      traffic:requests.models.Response - Object with traffic info
      repo:str - repository name 
   :sample: 
   {
        "timestamp" : "2018-06-08T00:00:00Z"
        "key"       : "ff7a5466-7c0a-11e8-ab26-0800275d93ce"
        "asset"     : "github/repo_name/traffic"
        "readings"  : {"traffic"" : 18}
   }
   """
   traffic=traffic.json()
   data=[]
   for key in traffic['views']: 
      timestamp=datetime.datetime.strptime(key['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
      data.append({'timestamp' : str(timestamp), 
                   'key'       : str(uuid.uuid4()),
                   'asset'     : 'github/%s/traffic' % repo, 
                   'readings'  : {'traffic' : key['uniques']}
                 })
   return data

def read_commits(commits:requests.models.Response=None, repo:str='repo_name')->list:
   """
   Create list of JSON objects with commits (by timestamp) info
   :param: 
      commits:requests.models.Response - Object with commit info
      repo:str - repository name
   :sample: 
   {
        "timestamp" : "2018-06-18"
        "key"       : "ff7a5466-7c0a-11e8-ab26-0800275d93ce"
        "asset"     : "github/repo_name/commits"
        "readings"  : {"commits/timestamp" : 12}
   }
   """
   commits=commits.json()

   # Group by TIMESTAMP
   timestamps={} 
   for i in range(len(commits)): 
      timestamp=commits[i]['commit']['author']['date']
      timestamp=timestamp.split('T')[0]
      if timestamp not in timestamps: 
         timestamps[timestamp]=0 
      timestamps[timestamp]+=1 

   # Create file with JSON object based on timestamps dict 
   data=[]
   for timestamp in timestamps: 
      data.append({'timestamp' : str(timestamp),
                   'key'       : str(uuid.uuid4()),
                   'asset'     : 'github/%s/commits' % repo, 
                   'readings'  : {'commits' : timestamps[timestamp]}
                 })
   return data 

def read_clones(clones:requests.models.Response=None, repo:str='repo_name')->list: 
   """
   Create list of JSON objects with daily clones, and write to file 
   :param: 
      clones:requests.models.Response - Object with clones info 
      repo:str - repository name
   :sample: 
   {
        "timestamp" : "2018-06-08"
        "key"       : "ff7a5466-7c0a-11e8-ab26-0800275d93ce"
        "asset"     : "github/repo_name/clones"
        "readings" : {"clones" : 5}
   }
   """
   clones=clones.json()
   data=[]
   for key in clones['clones']:
      data.append({'timestamp' : str(key['timestamp']),
                   'key'       : str(uuid.uuid4()),
                   'asset'     : 'github/%s/clones' % repo,
                   'readings'  : {'clones' : key['uniques']}
                 })
   return data 

def read_referrers(referrers:requests.models.Response=None, repo:str='repo_name', timestamp:str=datetime.datetime.now())->list:
   """
   Create a list of JSON objects with daily referrers 
   :param: 
      referrers:requests.models.Response - Object with referral info
      repo:str - reposiitory name
      timestamp:str - date when data is generated
   :sample:
   {
   }
   """

   referrers=referrers.json()
   data=[] 
   # {'count': 79, 'uniques': 19, 'referrer': 'Google'}
   for obj in referrers: 
      data.append({'timestamp': str(timestamp),
             'key': str(uuid.uuid4()),
             'asset': 'github/%s/referrerals/%s' % (repo, obj['referrer']), 
             'readings': {'count': obj['uniques'], # unique 
                          'total': obj['count'] 
                         }
           })
   return data

def write_to_file(file_name:str='/tmp/data.json', data:list=[]):
   """
   Write data into JSON file 
   :args: 
      file_name:str - File to store JSON data into 
      data:list - list of JSON objects
   """
   with open(file_name, 'a') as f:
      for obj in data:
         f.write(json.dumps(obj))
         f.write('\n')

def main():
    """
    Main
    :positional arguments:
       auth_file             authentication file
       port                  FogLAMP POST Port

    :optional arguments:
       -h, --help            show this help message and exit
       -d DIR, --dir DIR     directory to send data into (for JSON)

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('auth_file', default='$HOME/foglamp-south-plugin/GitHub_Data_Generator/other/auth_pair.txt', help='authentication file')
    parser.add_argument('-d', '--dir', default='/tmp', help='directory to send data into (for JSON)')
    args = parser.parse_args()

    env=os.path.expanduser(os.path.expandvars(args.auth_file))
    with open(env, 'r') as f:
       output=f.read().replace('\n','').split(' ')
    auth=(str(output[0].split(':')[0]), str(output[0].split(':')[-1]))
    repo=output[1]
    org=output[2]
    json_dir=output[3]

    # Generate data 
    timestamp_que=queue.Queue()
    traffic_que=queue.Queue()
    commits_que=queue.Queue()
    clones_que=queue.Queue()
    referrers_que=queue.Queue()
    
    threads=[
             threading.Thread(target=get_timestamp, args=(timestamp_que,)), 
             threading.Thread(target=send_request,   args=(traffic_que, commits_que, clones_que, referrers_que, repo, org, auth,))
            ]
    for thread in threads: 
       thread.start()
    for thread in threads: 
       thread.join()
 
    timestamp=timestamp_que.get()
    traffic=traffic_que.get()
    commits=commits_que.get()
    clones=clones_que.get()
    referrers=referrers_que.get() 

    file_name=args.dir+'/%s_%s_data.json' % (timestamp.replace(' ','_').replace(':', '_'), repo)
    write_to_file(file_name, read_traffic(traffic, repo))
    write_to_file(file_name, read_commits(commits,repo))
    write_to_file(file_name, read_clones(clones, repo)) 
    write_to_file(file_name, read_referrers(referrers, repo, timestamp.split(' ')[0]))




if __name__ == '__main__': 
   main()
