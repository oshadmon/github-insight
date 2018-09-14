import argparse
import boto3 
import datetime 
import psycopg2
import re


class AWSData: 
   def __init__(self, bucket_name:str='demo'): 
      """
      Use boto3 to retrieve data from AWS & send it to database
      :args: 
      :param: 
         self.bucket_name:str                - s3 bucket with data 
      """
      self.bucket_name=bucket_name 

   def read_data(self): 
      """
      Itterate through a given S3 bucket, copy data over into your local machine under /tmp
      """
      s3 = boto3.resource('s3')
      dir_name='/tmp/%s_aws' % datetime.datetime.now().strftime('%Y_%m_%d')
      os.system('rm -rf %s; mkdir %s' % (dir_name, dir_name)) 
      for obj in s3.Bucket(self.bucket_name).objects.all():
         file_name=dir_name+'/'+str(obj.key)
         with open(file_name, 'a') as f: 
            f.write(obj.get()['Body'].read())
def main(): 
   """
   Main 
   :positional arguments:
      bucket      AWS S3 bucket with data
   """
   parser = argparse.ArgumentParser()
   parser.add_argument('bucket',               default='new-bucket',          help='AWS S3 bucket with data') 
   args = parser.parse_args()

   aws=AWSData(bucket_name=args.bucket) 
   aws.read_data()
 
if __name__ == '__main__': 
   main() 
