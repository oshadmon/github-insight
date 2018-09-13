DROP TABLE IF EXISTS aws_downloads; 
CREATE TABLE aws_downloads( 
   create_date DATE NOT NULL DEFAULT CURRENT_TIMESTAMP, 
   ip          VARCHAR(255) NOT NULL DEFAULT '127.0.0.1'
); 

