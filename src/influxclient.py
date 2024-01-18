import json
from datetime import datetime
from influxdb import InfluxDBClient as InfluxDBClientV1
from influxdb.exceptions import InfluxDBClientError as InfluxDBClientErrorV1
from requests.exceptions import ConnectionError
from urllib3.exceptions import LocationValueError

from influxdb_client import InfluxDBClient as InfluxDBClientV2
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

class influxClient:
    def __init__(self, url=None, host=None, port=None, user=None, password=None, base=None, org=None, token=None, bucket=None, debug=False) -> None:
        self.__debug=debug
        self.__version=""
        self.__url=url

        if host != "":
            self.__version="V1"
            print("[influx] V1")
        elif url is not None or org is not None or token is not None or bucket is not None:
            self.__version="V2"
            print("[influx] V2")
            
        if self.__version == "V1":
            self.client = InfluxDBClientV1(host, port, user, password, base)
                    # Database create
            try:
                #self.client.drop_database(base)
                if any(base in entry['name'] for entry in self.client.get_list_database()):
                    print(f"[influx] Database {base} found")
                else:
                    print(f"[influx] Database {base} not found")
                    self.client.create_database(base)
                    print(f"[influx] Database {base} create")
            except ConnectionError as e:
                print("[influx] ConnectionError:",e)
        else:
            self.__version="V2"
            self.client = InfluxDBClientV2(url=url, token=token, org=org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.bucket = bucket


        
    def __del__(self):
        self.client.close()
        print("[influx] ... DEL")
        

    def nhc2_device_status_type_value (self,propertie) -> dict:
        out = {}
        for cle in propertie: 
            #Exetption
            if cle == "Status":
                out[cle] = propertie[cle]
                break

            #Int
            if propertie[cle].isdigit():
                out[cle] = int(propertie[cle])
                break
            #Float
            try:
                out[cle] = float(propertie[cle])
                break
            except ValueError:
                pass
            #Bool
            if propertie[cle].lower() in ['true', 'false']:
                out[cle] = True if propertie[cle].lower() == 'true' else False
                break
            #Other
            out[cle] = propertie[cle]
        return out

    def nhc2_device_status(self,params,datetime_req=None):
        if self.__debug:
            print("[Influx] device status ...")
        if datetime_req is None:
            datetime_req=datetime.now()
        dt_str = int( (datetime_req.timestamp() * 1e9) + (datetime_req.microsecond * 1e3))
        json_body = []
        for param in params:
            for device in param["Devices"]:
                if self.__debug:
                    print("[Influx] device : ",device)
                if "Properties" in device:
                    json_measurement_device = {
                        "measurement": "device-event",
                        "tags": {
                            "uuid": device["Uuid"]
                        },
                        "time":dt_str,
                        "fields": {}
                    }
                    fieldsDict = {}
                    for propertie in device["Properties"]:
                        #print("[influx] : ",propertie)
                        fieldsDict.update(self.nhc2_device_status_type_value(propertie))
                    json_measurement_device["fields"]=fieldsDict
                    json_body.append(json_measurement_device)
                if "Online" in device:
                    json_measurement_device = {
                        "measurement": "device-event",
                        "tags": {
                            "uuid": device["Uuid"]
                        },
                        "time":dt_str,
                        "fields": {"Online":bool(device["Online"])}
                    }
                    json_body.append(json_measurement_device)
        try:
            if self.__debug:
                print("[Influx] payload : ",json_body)

            if self.__version == "V1":
                self.client.write_points(json_body)
            elif self.__version == "V2":
                self.write_api.write(bucket=self.bucket, record=json_body)
            else:
                print("[Influx] ERROR Version")

            if self.__debug:
                print("[Influx] Write")
        except NameError:
            print("[Influx] BODY : ",json_body)
            print("[Influx] ERROR :",NameError)
        except InfluxDBClientErrorV1 as e:
            print("[Influx] BODY : ",json_body)
            print("[Influx] ERROR : An InfluxDBClientError occurred:",e)
        except ConnectionError as e:
            print("[influx] ConnectionError:",e)
        except LocationValueError as e:
            print("[influx] ConnectionError: Check URL (exemple : \"http://localhost:8086\" ) : ", self.__url)
            print("[influx] ConnectionError: ",e)
