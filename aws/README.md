# aws insight
Given an AWS S3 bucket with files contatining IPs and timestamps, retrieve the two and store in a database. 

# Prerequisites 
* [Python3](https://www.python.org/downloads/) 
* [pip3](https://pip.pypa.io/en/stable/installing/)
* [boto3](https://aws.amazon.com/sdk-for-python/) 
* [aws command-line](https://aws.amazon.com/cli/) 

# Configure AWS 
```
# Make sure everything is up to date 
sudo apt-get update 
sudo apt-get -y upgrade 
sudo apt-get update

# Install aws command line 
sudo apt install awscli

# Configure aws 
aws configure

# Install boto3
pip install boto3
```

# Files & Sample code
```create_table.sql``` - SQL with create table for aws_insight.py 
```aws_insight.py``` - Code that reads data bucket and stores it in database 
```
ubuntu@ori-foglamp:~/github-insight$ python3 aws/aws_insight.py --help
usage: aws_insight.py [-h] usr hst db bucket

positional arguments:
  usr         user/password to database [root:passwd]
  hst         host/port to database [localhost:5432]
  db          database name [test]
  bucket      AWS S3 bucket with data

optional arguments:
  -h, --help  show this help message and exit

ubuntu@ori-foglamp:~/github-insight$ python3 aws/aws_insight.py ubuntu:foglamp 127.0.0.1:5432 test
``` 
```sample.txt``` - Sample file with how files in AWS S3 bucket currently need to look to be read
```
ubuntu@ori-foglamp:~/github-insight$ cat aws/sample.txt 
b'94b0d7bdce49506054db00c7ed077b7600249ec3841c7afff89cdc3f06544e61 demo [26/Jan/2018:14:58:44 +0000] 88.97.58.233 94b0d7bdce49506054db00c7ed077b7600249ec3841c7afff89cdc3f06544e61 394718876F1C11F2 REST.GET.ENCRYPTION - "GET /demo?encryption= HTTP/1.1" 404 ServerSideEncryptionConfigurationNotFoundError 350 - 19 - "-" "S3Console/0.4, aws-internal/3" -\n'
```

