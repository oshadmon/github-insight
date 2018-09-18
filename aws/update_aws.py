import argparse
import psycopg2
def create_connection(hp:str='127.0.0.1:5432', up:str='ubuntu:foglamp', db:str='github')->psycopg2.extensions.cursor:
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

def aws_downloads(cur:psycopg2.extensions.cursor=None): 
   """
   Based on aws_ip_list generate aws_downloads
   :param:
      cur:psycopg2.extensions.cursor - connection to database
   """
   drop_table="DROP TABLE IF EXISTS aws_downloads;"
   create_table=("CREATE TABLE aws_downloads("
                +"timestamp DATE     NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                +"repo        VARCHAR  NOT NULL DEFAULT 'AWS',"
                +"today       INT      NOT NULL DEFAULT 0,"
                +"total       INT      NOT NULL DEFAULT 0"
                +");")
   insert_stmt="INSERT INTO aws_downloads(timestamp, today) SELECT create_date, COUNT(ip) FROM aws_ip_list GROUP BY create_date ORDER BY create_date;"
   cur.execute(drop_table) 
   cur.execute(create_table) 
   cur.execute(insert_stmt) 

def get_timestamps(cur:psycopg2.extensions.cursor=None)->list: 
   """
   Get list of timestamps from table
   :param: 
      cur:psycopg2.extensions.cursor - connection to database
      table_name:str - table to get timestamps from
   :return: 
      list of timsetamps 
   """
   get_timestamps_stmt="SELECT DISTINCT(timestamp) FROM aws_downloads ORDER  BY timestamp;" 
   cur.execute(get_timestamps_stmt)
   return cur.fetchall() 

def update_table(cur:psycopg2.extensions.cursor=None, timestamps:str=[]): 
   """
   Update timestamps
   :param: 
      cur:psycopg2.extensions.cursor - connection to database 
      timstamps:list - list of timestamps to update
      table_name:str - table to update 
   """
   update_values_stmt  = "UPDATE aws_downloads SET total=(SELECT SUM(today) FROM aws_downloads WHERE timestamp<='%s') WHERE timestamp='%s'"
   for timsetamp in timestamps: 
      cur.execute(update_values_stmt % (timsetamp[0], timsetamp[0]))

def main(): 
   """
   Main
   """
   parser = argparse.ArgumentParser()
   parser.add_argument('-usr', '--usr', default='ubuntu:foglamp', help='db user and password')
   parser.add_argument('-hst', '--hst', default='127.0.0.1:5432', help='db host and port') 
   parser.add_argument('-dbn', '--dbn', default='test',           help='db name') 
   args = parser.parse_args()

   cur=create_connection(args.hst, args.usr, args.dbn)
   aws_downloads(cur) 
   timestamps=get_timestamps(cur)
   update_table(cur, timestamps)
   
if __name__ == '__main__':
   main()
