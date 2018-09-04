#!/bin/user/python
"""
Name: Ori Shadmon
Date: August 2018 
Description: The following code takes github insight (generated by generate_github_data.py) and send it to database  
"""
import argparse
import json
import psycopg2

class SendData: 
   def __init__(self, file_name:str='/tmp/data.json', hp:str='127.0.0.1:5432', up:str='ubuntu:foglamp', db:str='github'): 
      """
      Send data generated from GitHub into tables
      :param:
         file_name:str - file containing data from GitHub
         hp:str - database node host & port
         up:str - database user & password
         db:str - database name where tables are stored
      """
      self.file_name=file_name
      self.data={
         'traffic':   [],
         'clones':    [],
         'commits':   [],
         'referrals': [],
      }
      self.read_data()
      self.cur=self.create_connection(hp=hp, up=up, db=db) 

   def read_data(self):
      """
      Write lines in JSON data file into dict with keys corresponding to assets
      """
      with open(self.file_name, 'r') as f: 
         for line in f.read().split('\n'):
            if line != '': 
               if 'traffic' in json.loads(line)['asset']: 
                  self.data['traffic'].append(json.loads(line))
               elif 'clones' in json.loads(line)['asset']:
                  self.data['clones'].append(json.loads(line))
               elif 'commits' in json.loads(line)['asset']:
                  self.data['commits'].append(json.loads(line))
               elif 'referrerals' in json.loads(line)['asset']:
                  self.data['referrals'].append(json.loads(line))

   def create_connection(self, hp:str='127.0.0.1:5432', up:str='ubuntu:foglamp', db:str='github')->psycopg2.extensions.cursor: 
      """
      Create connection to database 
      :param: 
         hp:str - host and password 
         up:str - username and password
         db:str - database name
      :return:
         executable connection to database
      """
      conn=psycopg2.connect(host=hp.split(':')[0], port=int(hp.split(':')[1]), user=up.split(':')[0], password=up.split(':')[1], dbname=db)
      conn.autocommit=True
      return conn.cursor()

   def check_row(self, table_name:str='github', timestammp:str='2000-01-01', repo:str='new repo', referral:str='github.com')->int: 
      """
      check whether or not row already exists in a given table
      :param:
         table_name:str - table name
         timestamp:str - row timestamp
         repo:str - row repo
         referral:str - for github_referral table row referral
      :return: 
         count of table (expect 0) 
      """ 
      if table_name == 'github_referrals2':
         stmt="SELECT COUNT(*) FROM %s WHERE timestamp='%s' AND repo='%s' AND referral='%s';" 
         self.cur.execute(stmt % (table_name, timestammp, repo, referral))
      else: 
         stmt="SELECT COUNT(*) FROM %s WHERE timestamp='%s' AND repo='%s';"
         self.cur.execute(stmt % (table_name, timestammp, repo)) 
      return int(self.cur.fetchall()[0][0])

   def create_tables(self, tables_file:str='/tmp/tables.sql'):
      """
      Create tables from file
      """ 
      self.cur(open(tables_file, 'r').read())

   def insert_traffic(self): 
      """
      insert into github_traffic2 table
      """
      inst_stmt="INSERT INTO github_traffic2(row_id, timestamp, repo, today) VALUES ('%s', DATE('%s'), '%s', %s);"
      updt_stmt="UPDATE github_traffic2 SET total=(SELECT SUM(today) FROM github_traffic2 WHERE repo='%s' AND timestamp<='%s') WHERE repo='%s' AND timestamp='%s';"
      for obj in self.data['traffic']:
         row_id=obj['key']
         timestamp=obj['timestamp']
         repo=obj['asset'].split('/')[1]
         traffic=obj['readings']['traffic']
         if self.check_row('github_traffic2', timestamp, repo) == 0:# check if already exists - if not: 
            self.cur.execute(inst_stmt % (row_id, timestamp, repo, traffic)) # INSERT 
            self.cur.execute('commit;') 
            self.cur.execute(updt_stmt % (repo, timestamp, repo, timestamp))
            self.cur.execute('commit;') 
 
   def insert_clones(self):
      """
      insert into github_clones2 table 
      """
      inst_stmt="INSERT INTO github_clones2(row_id, timestamp, repo, today) VALUES ('%s', DATE('%s'), '%s', %s);"
      updt_stmt="UPDATE github_clones2 SET total=(SELECT SUM(today) FROM github_clones2 WHERE repo='%s' AND timestamp<='%s') WHERE repo='%s' AND timestamp='%s';"
      for obj in self.data['clones']:
         row_id=obj['key'] 
         timestamp=obj['timestamp']
         repo=obj['asset'].split('/')[1]
         clones=obj['readings']['clones']

         if self.check_row('github_clones2', timestamp, repo) == 0: 
            self.cur.execute(inst_stmt % (row_id, timestamp, repo, clones)) 
            self.cur.execute('commit;') 
            self.cur.execute(updt_stmt % (repo, timestamp, repo, timestamp))
            self.cur.execute('commit;')

   def insert_commits(self): 
      """
      insert into github_commits2 table
      """
      inst_stmt="INSERT INTO github_commits2(row_id, timestamp, repo, today) VALUES ('%s', DATE('%s'), '%s', %s);"
      updt_stmt="UPDATE github_commits2 SET total=(SELECT SUM(today) FROM github_commits2 WHERE repo='%s' AND timestamp<='%s') WHERE repo='%s' AND timestamp<='%s'"
      for obj in self.data['commits']:
         row_id=obj['key']
         timestamp=obj['timestamp']
         repo=obj['asset'].split('/')[1]
         commits=obj['readings']['commits']
         if self.check_row('github_commits2', timestamp, repo) == 0:
            self.cur.execute(inst_stmt % (row_id, timestamp, repo, commits))
            self.cur.execute('commit;')
            self.cur.execute(updt_stmt % (repo, timestamp, repo, timestamp))
            self.cur.execute('commit;') 

   def insert_referrals(self):
      """
      insert into github_referrals2
      """
      inst_stmt="INSERT INTO github_referrals2(row_id, timestamp, repo, referral, today) VALUES('%s', DATE('%s'), '%s', '%s', %s);"
      updt_stmt=("UPDATE github_referrals2 SET total=("
                   +"SELECT SUM(today) FROM github_referrals2 WHERE repo='%s' AND referral='%s' AND timestamp<='%s'"
                +") WHERE row_id='%s';")
      for obj in self.data['referrals']: 
         row_id=obj['key']
         timestamp=obj['timestamp']
         repo=obj['asset'].split('/')[1]
         referral=obj['asset'].split('/')[-1]
         today=obj['readings']['count']

         if self.check_row('github_referrals2', timestamp, repo, referral) == 0: 
            self.cur.execute(inst_stmt % (row_id, timestamp, repo, referral, today))
            self.cur.execute('commit;')
            self.cur.execute(updt_stmt % (repo, referral, timestamp, row_id))
            self.cur.execute('commit;')

def main(): 
   """
   Main
   :positional arguments:
      file_name           file with data from github
   :optional arguments:
      -h,  --help         show this help message and exit
      -up, --up           user & password for database
      -hp, --hp           host & port for database
      -db, --db           database name for database
      -create, --create   SQL file with create tables
   """
   parser = argparse.ArgumentParser()
   parser.add_argument('file_name',   default='/tmp/github_data.json', help='file with data from github')
   # Database connection info
   parser.add_argument('-up', '--up',         default='usr:passwd',            help='user & password for database') 
   parser.add_argument('-hp', '--hp',         default='127.0.0.1:5432',        help='host & port for database') 
   parser.add_argument('-db', '--db',         default='github',                help='database name for database') 
   parser.add_argument('-create', '--create', default=None,                      help='SQL file with create tables') 
   args = parser.parse_args()
 
   sd=SendData(args.file_name, args.hp, args.up, args.db) 
   if args.create is not None: 
      sd.create_tables(args.create) 
   sd.insert_traffic() 
   sd.insert_clones() 
   sd.insert_commits() 
   sd.insert_referrals() 

if __name__ == '__main__': 
   main()
