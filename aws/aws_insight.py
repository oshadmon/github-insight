import argparse
import boto3 
import datetime 
import psycopg2
import re


class AWSData: 
   def __init__(self, bucket_name:str='demo', up:str='user:passwd', hp:str='127.0.0.1:5432', dbname:str='test'): 
      """
      Based on information from AWS store the IP address & timestamp in aws_ip_list if value set DNE 
      :args: 
         up:str          - database username/password
         hp:str          - database host/port 
         dname:str       - databse name 
      :param: 
         self.bucket_name:str                - s3 bucket with data 
         self.cur:psycopg2.extensions.cursor - connection to database 
      """
      self.bucket_name=bucket_name 
      self.cur=self.__create_connection(up, hp, dbname)
      self.ip_dict={}

   def __create_connection(self, usr:str='root:passwd',
                           hst:str='localhost:54321', db:str='test')->psycopg2.extensions.cursor:
      """
      Create connection
      :param:
         usr:str - user & passwd to connect to database 
         hst:str - host & port to connection to databse
         db:str  - database name
      :return: 
         connection to database 
      """
      conn=psycopg2.connect(host=hst.split(':')[0], port=int(hst.split(':')[1]), user=usr.split(':')[0], password=usr.split(':')[1], dbname=db)
      conn.autocommit=True
      return conn.cursor()

   def check_table(self, ip:str='127.0.0.1', date:str='2000-01-01'): 
      """ 
      check if row with given ip & timestamp exits
      :param: 
         ip:str - IP of user 
         date:str - date IP accessed us 
      :return: 
         1 if row exist otherwise 0
      """
      stmt="SELECT COUNT(*) FROM aws_ip_list WHERE ip='%s' AND create_date='%s'" % (ip, date)
      self.cur.execute(stmt)
      return self.cur.fetchall()[0][0]

   def write_to_table(self,ip:str='127.0.0.1', date:str='2000-01-01'): 
      """
      Execute INSERT 
      :param: 
         ip:str - IP of user 
         date:str - date IP accessed us 
      """ 
      stmt="INSERT INTO aws_ip_list VALUES('%s', '%s');" 
      self.cur.execute(stmt % (date, ip))
      self.cur.execute('commit;')

   def get_data(self): 
      """
      itterate through a given S3 bucket containing files with IP and timestamp, and retrieve the IP and timestamp.
      sample.txt is a sample file of what the code can work with. 
      """
      s3 = boto3.resource('s3')
      for obj in s3.Bucket(self.bucket_name).objects.all():
         output=str(obj.get()['Body'].read())
         ip=re.findall( r'[0-9]+(?:\.[0-9]+){3}', output)[0] 
         date=output.split(' [')[-1].split(':')[0] 
         date=datetime.datetime.strptime(date, "%d/%b/%Y")
         if int(self.check_table(ip, date)) == 0: 
            self.write_to_table(ip, date)
def main(): 
   """
   Main 
   :positional arguments:
      usr         user/password to database [root:passwd]
      hst         host/port to database [localhost:5432]
      db          database name [test]
      bucket      AWS S3 bucket with data
   """
   parser = argparse.ArgumentParser()
   parser.add_argument('usr',                  default='root:passwd',         help='user/password to database [root:passwd]')
   parser.add_argument('hst',                  default='localhost:5432',      help='host/port to database [localhost:5432]')
   parser.add_argument('db',                   default='test',                help='database name [test]')
   parser.add_argument('bucket',               default='new-bucket',          help='AWS S3 bucket with data') 
   args = parser.parse_args()

   aws=AWSData(bucket_name=args.bucket, up=args.usr, hp=args.hst, dbname=args.db) 
   aws.get_data()
 
if __name__ == '__main__': 
   main() 
