CREATE TABLE GitHub_Traffic(
   `key`           VARCHAR(255) NOT NULL DEFAULT '',
   `timestamp`     TIMESTAMP    NOT NULL DEFAULT '0000-00-00 00:00:00', 
   `repo`          VARCHAR(255) NOT NULL DEFAULT 'new repo', 
   `traffic`       INT          NOT NULL DEFAULT 0, 
   `total traffic` INT          NOT NULL DEFAULT 0, 
   PRIMARY KEY `key_pk` (`key`)
); 

CREATE TABLE GitHub_Commits(
   `key`           VARCHAR(255) NOT NULL DEFAULT '',
   `timestamp`     TIMESTAMP    NOT NULL DEFAULT '0000-00-00 00:00:00', 
   `repo`          VARCHAR(255) NOT NULL DEFAULT 'new repo',
   `user_name`     VARCHAR(255) NOT NULL DEFAULT 'all users',
   `commits`       INT          NOT NULL DEFAULT 0, 
   `total commits` INT          NOT NULL DEFAULT 0,
   PRIMARY KEY `key_pk`(`key`)
); 

CREATE TABLE GitHub_Clones(
   `key`           VARCHAR(255) NOT NULL DEFAULT '',
   `timestamp`     TIMESTAMP    NOT NULL DEFAULT '0000-00-00 00:00:00', 
   `repo`          VARCHAR(255) NOT NULL DEFAULT 'new repo',
   `clones`        INT          NOT NULL DEFAULT 0, 
   `total clones`  INT          NOT NULL DEFAULT 0, 
   PRIMARY KEY `key_pk`(`key`)
); 


   
