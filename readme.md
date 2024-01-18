![version](https://img.shields.io/badge/licence-GNU-blue)
![version](https://img.shields.io/badge/version-v0.1.3-green)

# NHC2 To Grafana

This project sends all information from control unit 2 by Niko Home Control to Influxdb, and it's read by Grafana.

![schema](docs/schema.png)

## Quick start
```
$ nano .nhc2influx.env
```
```
NHC2_HOST="FP<MAC-Address>"
NHC2_PASS="<JWT>"
INFLUXDB_HOST="127.0.0.1"
```
```
$ docker run --env-file .nhc2influx.env mon_image
```


## Install
**Requirements**
- influxdb 1.8
- grafana OSS

## Setup
- Define environmental variables in docker-compose
- Start docker-compose
- 

## Build
```
$ docker build -t nhc2influxdb:latest . 
$ docker compose up -d
```
## Developper

```
$ python3 -m venv env
$ source env/bin/activate
$ pip install --no-cache-dir -r requirements.txt
```