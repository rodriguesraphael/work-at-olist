
Description
===========
Proposed solution to the [Olist challenge](https://github.com/olist/work-at-olist).

Instalation
===========
```bash
git clone https://github.com/rodriguesraphael/work-at-olist
cd work-at-olist/
virtualenv env -p python3
source env/bin/activate
```

Environment Variables
=====================
*[Dynaconf](https://dynaconf.readthedocs.io/en/latest/) was used to manage Django's environment variables and settings. 
Before starting the application create a .env file with the variables needed to start Django, you can copy the example contained in the repository, see the example below.*
```bash
cp .env.example .env
```

*Or you can export the variables in the environment.*
```bash
export BILLCALLS_ENV=development
export BILLCALLS_SECRET_KEY="CHANGE_ME!!!! (P.S. the SECRET_KEY environment variable will be used, if set, instead)."
export BILLCALLS_DEBUG=true
export BILLCALLS_ALLOWED_HOSTS=*
```

Deploy in Develop Environment
============================
```bash
pip install -r requirements-dev.txt
./manage.py migrate
```

Load Sample Data
================
```bash
./manage.py loaddata calls/fixtures/fixture-calls.json
```

Run Tests
=========
```bash
./manage.py test
```

Deploy in Docker
================
```bash
docker-compose run web ./manage.py migrate
docker-compose up
```
*To execute commands in the application do as in the example below*
```bash
docker-compose run web ./manage.py test
docker-compose run web ./manage.py loaddata calls/fixtures/fixture-calls.json
```
Usage Examples
==============
**POST START CALL**
```bash
curl -i -X POST https://billcalls.herokuapp.com/call-log/ \
        -H 'Content-Type: application/json' \
        -d '{
            "call_id": 100,
            "source": "41888889999",
            "destination": "41999998888",
            "timestamp": "2018-11-20T15:20:12Z",
            "type": "start"
        }'
```

**POST END CALL**
```bash
curl -i -X POST https://billcalls.herokuapp.com/call-log \
        -H 'Content-Type: application/json' \
        -d '{
            "call_id": 100,
            "timestamp": "2018-11-20T15:25:42Z",
            "type": "end"
        }'
```

**GET TELEPHONE BILL**

*Use query argument 'date=mmYYYY' to search by date
e.g.*
```bash
curl -i -X GET https://billcalls.herokuapp.com/call-invoice/41888889999?date=112018

[{"call_id":100,"price":"R$ 0.81","duration":"0h5m30s","call_start_date":"2018-11-20","call_start_time":"15:20:12","destination":"41999998888"}]
```

*If the reference date is not entered, the previous month will be consulted.*
```bash
curl -i -X GET https://billcalls.herokuapp.com/call-invoice/41888889999
```

Working Enviroment Used
=======================
|||
| --- | --- |
|OS System | Debian |
|Description | Debian GNU/Linux 9.11 (stretch)|
|Release | 9.11|
|Codename | stretch|

**Text Editor/IDE**

|||
| --- | --- |
|PyCharm 2018.3.2 (Community Edition)|
|Build #PC-183.4886.43, built on December 18, 2018|
|JRE: 1.8.0_152-release-1343-b26 amd64|
|JVM: OpenJDK 64-Bit Server VM by JetBrains s.r.o|
|Linux 4.9.0-11-amd64|

**Libraries**
|||
| --- | --- |
|Python 3.7
|Django 2.2.5
|djangorestframework 3.10.3
|coreapi 2.3.3
|dynaconf
