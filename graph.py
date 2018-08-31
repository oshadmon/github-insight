import argparse
import datetime 
import os
import plotly.offline as offline
import psycopg2
import sys 

from plotly.graph_objs import *
import plotly.plotly as py 

class GenerateGraph: 
   def __init__(self, cur=None, data_dir='/var/www/html', title='Grapph 1',
                total_only = False, daily_only=False,
                query='SELECT create_timestamp, COUNT(*)  FROM t1 GROUP BY create_timestamp ORDER BY create_timestamp;'
               ):
                
      """
      Generate graphs based on the results in database 
      :param: 
         self.cur             - connection to database 
         self.data_dir:str    - file in which graph will be stored 
                                Note, Plot.ly rewrites file rather than append 
         self.title:str       - Graph title
         self.type:str        - Graph type (either line or bar graph) 
         self.query:str       - Query against the original table to generate graphs 
         self.total_only:bool - generate only cumulative results 
         self.daily_only:nool - generate only non-cumulative results   

      """
      self.cur = cur 
      self.data_dir = data_dir
      self.title = title 
      self.query = query 
      self.total_only = total_only 
      self.daily_only = daily_only 
   
   def drop_temp_table(self): 
      """
      Drop temporary table 
      """
      self.cur.execute("DROP TABLE IF EXISTS temp_data") 

   def create_temp_table(self): 
      """
      Create temporary table from which graphs will be generated 
      """
      create_table = ("CREATE TEMPORARY TABLE temp_data(" 
                     +"\n\txaxy VARCHAR(255) DEFAULT ''," 
                     +"\n\tuniques FLOAT NOT NULL DEFAULT 0.0,"
                     +"\n\ttotal FLOAT NOT NULL DEFAULT 0.0\n);"
                     )
      self.cur.execute(create_table)
   
   def generate_data_to_graph(self): 
      insert_stmt = "INSERT INTO temp_data(xaxy, uniques, total) VALUES ('%s', '%s', '%s');"  
      total = 0 

      self.cur.execute(self.query)
      for result in self.cur.fetchall():
         total += result[1]
         self.cur.execute(insert_stmt % (result[0], result[1], total)) 

   def __retrieve_data(self, query='SELECT xaxy, uniques, total FROM temp_data ORDER BY xaxy'): 
      results = []
      i = 0
      self.cur.execute(query) 
      for result in self.cur.fetchall():
         results.append(result)
      self.cur.close() 
      column={}
      for v in range(len(results[0])):
        column[v]=[]
      for result in results: 
         for key in column.keys(): 
            column[key].append(result[key])
      return column

   def draw_line_graph(self): 
     """
     Based on the results in the table, graph the output
     :args: 
        columns:dict - Dictionary of columns that are being used. 
                       Note that 0 key in columns is the X-axy, all else relate to Y-axy
        layout:Layout - Layout of graph 
        names:list - List of trace names 
     """ 
     xaxy = self.query.split("SELECT")[-1].split(",",1)[0].replace(" ","")
     yaxy = "count" 
     file_name = self.data_dir+"/"+str(datetime.datetime.now()).split(" ")[0].replace("-","_")+"_"+self.title.replace(" ", "_")+".html"
     if self.daily_only is True and self.total_only is False: 
        columns = self.__retrieve_data("SELECT xaxy, uniques FROM temp_data ORDER BY xaxy;")
        trace_names = ['daily']
     elif self.total_only is True and self.daily_only is False: 
        columns = self.__retrieve_data("SELECT xaxy, total FROM temp_data ORDER BY xaxy;") 
        trace_names = ['total'] 
     else: 
        columns = self.__retrieve_data()
        trace_names = ['daily', 'total'] 
     # Generate trace lines
     traces = [] 
     for key in range(1, len(columns)): 
        traces.append(Scatter(x=columns[0], y=columns[key], name=trace_names[key-1])) 
     # Layout 
     layout = Layout( 
           title=self.title,
           xaxis=dict(title=xaxy), 
           yaxis=dict(title=yaxy), 
     )
     # Draw 
     data = Data(traces) 
     fig = Figure(data=data, layout=layout)
     offline.plot(fig, filename=file_name)
     # Write query at the bottom of the graph
     f = open(file_name, 'a') 
     f.write("<body><div><center>"+self.query+"</center></div></body>")
     f.close()

   def draw_horizontal_bar_graph(self): 
     """
     Based on the results in the table, graph the output
     :args: 
        columns:dict - Dictionary of columns that are being used. 
                       Note that 0 key in columns is the X-axy, all else relate to Y-axy
        layout:Layout - Layout of graph 
        names:list - List of trace names 
     """
     xaxy = self.query.split("SELECT")[-1].split(",",1)[0].replace(" ","")
     yaxy = "count"
     file_name = self.data_dir+"/"+str(datetime.datetime.now()).split(" ")[0].replace("-","_")+"_"+self.title.replace(" ", "_")+".html"
     if self.daily_only is True and self.total_only is False:
        columns = self.__retrieve_data("SELECT xaxy, uniques FROM temp_data ORDER BY xaxy;")
        trace_names = ['daily']
     elif self.total_only is True and self.daily_only is False:
        columns = self.__retrieve_data("SELECT xaxy, total FROM temp_data ORDER BY xaxy;")
        trace_names = ['total']
     else:
        columns = self.__retrieve_data("SELECT xaxy, uniques, total FROM temp_data ORDER BY xaxy;")
        trace_names = ['daily', 'total']
     # Generate trace lines
     traces = []
     for key in range(1, len(columns)):
        traces.append(Bar(x=columns[key], y=columns[0], orientation='h'))
     # Layout 
     layout = Layout(
           title=self.title,
           xaxis=dict(title=yaxy),
           yaxis=dict(title=xaxy),
     )

     # Draw 
     data = Data(traces)
     fig = Figure(data=data, layout=layout)
     offline.plot(fig, filename=file_name)
     f = open(file_name, 'a')
     f.write("<body><div><center>"+self.query+"</center></div></body>")
     f.close() 

   def draw_pie_graph(self): 
      """
      Based on results in the table, graph the output as pie graph
      :args: 
         data:dcit - Dictionary containing both labels and values being used 
      """
      file_name = self.data_dir+"/"+str(datetime.datetime.now()).split(" ")[0].replace("-","_")+"_"+self.title.replace(" ", "_")+".html"
      data = self.__retrieve_data(self.query)
      fig = {
         'data': [
            {
               'labels': data[0], 
               'values': data[1], 
               'type': 'pie', 
               'name': self.title, 
               'hoverinfo': 'label+percent', 
               'textinfo': 'none',
               'marker': { 
                  'colors': ['rgb(151, 154, 154)',
                             'rgb(217, 136, 128)',  
                             'rgb(230, 176, 170)', 
                             'rgb(242, 215, 213)',
                             'rgb(245, 183, 177)',
                             'rgb(249, 215, 213)',
                             'rgb(249, 235, 234)',
                             'rgb(250, 219, 216)',
                             'rgb(253, 237, 236)'
                  ]
               }
         }], 
         'layout': {
            'title': self.title,
            'showlegend': True
         }
      }
      offline.plot(fig, filename=file_name)
      f = open(file_name, 'a')
      f.write("<body><div><center>"+self.query+"</center></div></body>")
      f.close()


def __create_connection(host='127.0.0.1', port=5432, user='root', password='passwd', dbname='test'): 
   """
   Create connection to database
   :params:
      host:str - database host
      port:int - database port
      user:str - database user 
      password:str - database password 
      dbname: str - database name 
   :return:
      open connection to database
   """
   conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
   conn.autocommit = True
   return conn.cursor()

def main(): 
   """
   :positional arguments:
      host                  host/port connection to database [127.0.0.1:5432]
      user                  user/password to database [root:passwd]
      dbname                database name [test]
      html_file             File containing output image

   :optional arguments:
      -h,             --help       show this help message and exit
      --title         TITLE        Title of the graph
      --query         QUERY        Select statement to run against (2 values in select max)
      --total-only    TOTAL_ONLY   Graph only the cummulated values
      --daily-only    DAILY_ONLY   Dont graph the cummulated values
   """
   parser = argparse.ArgumentParser()
   parser.add_argument('host',      default='127.0.0.1:5432', help='host/port connection to database [127.0.0.1:5432]') 
   parser.add_argument('user',      default='root:passwd',    help='user/password to database [root:passwd]') 
   parser.add_argument('dbname',    default='test',           help='database name [test]')
   parser.add_argument('data_dir', default='/tmp/data.html', help='File containing output image') 
   # Optional
   parser.add_argument('--title', default='New Graph', help='Title of the graph') 
   parser.add_argument('--query', default='SELECT create_timestamp, COUNT(*) FROM t1 GROUP BY create_timestamp ORDER BY create_timestamp',
                        help='Select statement to run against (2 values in select max, where x-axy is first)') 
   parser.add_argument('--graph-type', default='line',           help='Type of graph to generate [line, hbar, pie]') 
   parser.add_argument('--total-only', default=False, type=bool, help='Graph only the cummulated values') 
   parser.add_argument('--daily-only', default=False, type=bool, help='Dont graph the cummulated values') 
   args = parser.parse_args()
   
   # Connect to database 
   cur = __create_connection(host=args.host.split(":")[0], port=int(args.host.split(":")[1]), 
                             user=args.user.split(":")[0], password=args.user.split(":")[1], 
                             dbname=args.dbname)

   gg = GenerateGraph(cur=cur, data_dir=args.data_dir, title=args.title, total_only=args.total_only, 
                      daily_only=args.daily_only, query=args.query)
    
   gg.drop_temp_table() 
   gg.create_temp_table() 
   gg.generate_data_to_graph() 
   if args.graph_type == 'line': 
      gg.draw_line_graph() 
   elif args.graph_type == 'hbar': 
      gg.draw_horizontal_bar_graph()
   elif args.graph_type == 'pie': 
      gg.draw_pie_graph() 

if __name__ == '__main__': 
   main()

