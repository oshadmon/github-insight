DROP TABLE IF EXISTS aws_downloads; 
CREATE TABLE aws_downloads( 
   create_date DATE     NOT NULL DEFAULT CURRENT_TIMESTAMP, 
   repo        VARCHAR  NOT NULL DEFAULT 'AWS', 
   ip_count    int  NOT NULL DEFAULT 0 
); 

INSERT INTO aws_downloads(create_date, ip_count) SELECT create_date, COUNT(ip) FROM aws_ip_list GROUP BY create_date ORDER BY create_date; 

