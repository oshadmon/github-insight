CREATE TABLE github_traffic(
   row_id    VARCHAR(255) NOT NULL DEFAULT 'c8e968cd-fb59-4d65-8f65-d88d9bf7b03c', 
   timestamp DATE         NOT NULL DEFAULT '2000-01-01',
   traffic   INT          NOT NULL DEFAULT 0, 
   total     INT          NOT NULL DEFAULT 0, -- value is calculated as SUM(traffic)
   PRIMARY KEY (row_id) -- This is "legal" only because column is really of UUID type
); 

CREATE TABLE github_commits(
   row_id VARCHAR(255) NOT NULL DEFAULT 'c8e968cd-fb59-4d65-8f65-d88d9bf7b03c',   
   timestamp DATE         NOT NULL DEFAULT '2000-01-01',
   commits   INT          NOT NULL DEFAULT 0,   
   total     INT          NOT NULL DEFAULT 0, -- value is calculated as SUM(commits)
   PRIMARY KEY (row_id) -- This is "legal" only because column is really of UUID type
);

CREATE TABLE github_clones(
   row_id    VARCHAR(255) NOT NULL DEFAULT 'c8e968cd-fb59-4d65-8f65-d88d9bf7b03c',   
   timestamp DATE         NOT NULL DEFAULT '2000-01-01',
   clones    INT          NOT NULL DEFAULT 0,   
   total     INT          NOT NULL DEFAULT 0, -- value is calculated as SUM(clones)
   PRIMARY KEY (row_id) -- This is "legal" only because column is really of UUID type
); 

CREATE TABLE github_referrals(
   row_id    VARCHAR(255) NOT NULL DEFAULT 'c8e968cd-fb59-4d65-8f65-d88d9bf7b03c',
   timestamp DATE         NOT NULL DEFAULT '2000-01-01',
   referral  VARCHAR(255) NOT NULL DEFAULT 'github.com',
   today     INT          NOT NULL DEFAULT 0, 
   total     INT          NOT NULL DEFAULT 0,
   PRIMARY KEY (row_id) -- This is "legal" only because column is really of UUID type
);



