import os
import time
import json
import traceback
import urllib.request
from dotenv import load_dotenv

import paho.mqtt.client as mqtt
from mqttclient import Nhc2Client
from influxclient import influxClient


################################################################ Env

load_dotenv()
DEBUG = False

NHC2_HOST = ""
NHC2_USER = "hobby"
NHC2_PASS = ""
NHC2_PORT = 8884
NHC2_CERT = "ca-chain.cert.pem"

INFLUX_HOST = ""
INFLUX_PORT = 8086
INFLUX_BASE ="nhc2"
INFLUX_USER = ""
INFLUX_PASS = ""

INFLUX_URL = ""
INFLUX_TOKEN = ""
INFLUX_ORG = ""
INFLUX_BUCKET = ""

def check_variable(var_name:set,conf:bool,required:bool,callback_notfound=None) -> bool:
    if var_name in os.environ:
        valeur_variable = os.environ[var_name]
        if conf is False:
            print(f"[ENV] {var_name} : {valeur_variable}")
        else:
            print(f"[ENV] {var_name} : Ok")
        globals()[var_name] = valeur_variable
        return True
    else:
        if callback_notfound is not None:
            if callback_notfound() is True:
                return True
        if required is False:
            return True
        print(f"[ENV] {var_name} : Not found")
        return False
    
def if_cert_not_found() -> bool:
    nhc2_url_ca_chain = "https://mynikohomecontrol.niko.eu/Content/hobbyapi/ca-chain.cert.pem"
    try:
        if os.path.isfile(NHC2_CERT) is False:
            urllib.request.urlretrieve(nhc2_url_ca_chain, NHC2_CERT)
            if os.path.isfile(NHC2_CERT):
                print(f"Downlaod certificat nhc2 hobbyapi Sucess")
                print(f"NHC2_CERT : Ok")
                return True
        else:
            print(f"[ENV] NHC2_CERT : Ok")
            return True
    except Exception as e:
        print(f"Downlaod certificat nhc2 hobbyapi Fail")
    return False
    

def check_all_variable() -> bool:
    ret = True
    ret &= check_variable("DEBUG",False,False)

    ret &= check_variable("NHC2_HOST",False,True)
    ret &= check_variable("NHC2_USER",False,False)
    ret &= check_variable("NHC2_PASS",True,True)
    ret &= check_variable("NHC2_PORT",False,False)
    ret &= check_variable("NHC2_CERT",False,True,if_cert_not_found)
    
    ret &= check_variable("INFLUX_HOST",False,False)
    ret &= check_variable("INFLUX_PORT",False,False)
    ret &= check_variable("INFLUX_BASE",False,False)
    ret &= check_variable("INFLUX_USER",False,False)
    ret &= check_variable("INFLUX_PASS",True,False)

    ret &= check_variable("INFLUX_URL",False,False)
    ret &= check_variable("INFLUX_TOKEN",True,False)
    ret &= check_variable("INFLUX_ORG",False,False)
    ret &= check_variable("INFLUX_BUCKET",False,False)
    return ret

################################################################ App
def mng_nhc_ctrl_dev_err(client, userdata, msg:mqtt.MQTTMessage):
    print(f"[APP Niko] MSG ERROR : {msg.topic}: {msg.payload.decode()}")

def mng_nhc_ctrl_dev_evt(client, userdata, msg:mqtt.MQTTMessage):
    print(f"[APP NHC2 EVT] {msg.topic}: {msg.payload.decode()}")
    
    try:
        payload = json.loads(msg.payload.decode())
        if payload["Method"] == "devices.status":
            __influx.nhc2_device_status(payload["Params"])
    except Exception as e:
        traceback.print_exc()
        print("[APP Niko] ERROR : mng_nhc_ctrl_dev_evt : ",e)


 ########################################### Main
# Test Env
if check_all_variable() is False:
    print("Set ERROR: Check environement variable")
    exit()

# Init
__influx = influxClient(host=INFLUX_HOST, port=INFLUX_PORT, password=INFLUX_PASS, base=INFLUX_BASE, user=INFLUX_USER, 
                        url=INFLUX_URL, org=INFLUX_ORG, bucket=INFLUX_BUCKET, token=INFLUX_TOKEN, debug=DEBUG)
__nhc = Nhc2Client(NHC2_HOST, NHC2_PORT, NHC2_USER, NHC2_PASS, NHC2_CERT,debug=DEBUG)

__nhc.add_callback("hobby/control/devices/evt",mng_nhc_ctrl_dev_evt)
__nhc.add_callback("hobby/control/devices/err",mng_nhc_ctrl_dev_err)

# Loop
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    del __nhc
    del __influx
    print("\nexit")
    exit()
finally:
    try:
        del __nhc
        del __influx
    except:
        pass
    print("\nEnd")
