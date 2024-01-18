import ssl
import json
import time
import traceback
import paho.mqtt.client as mqtt

#import logging
#logging.basicConfig(level=logging.DEBUG)


class Nhc2Client:
    def __init__(self, host, port, user, password, cert_file, debug=False):
        self.debug=debug
        self.__topic_sub = ["hobby/control/devices/evt", "hobby/control/devices/err"]
        self.__topic_sub_callback = {}
        self.__devicelist={}

        # Init
        try:
            self.client = mqtt.Client(client_id="nhc2-gateway", clean_session=True, userdata=None)
            self.client.on_connect = self.__on_connect
            self.client.on_message = self.__on_message
            #if debug is True:
            #    self.client.enable_logger(logger=None)
            try:
                self.client.tls_set(ca_certs=cert_file, tls_version=ssl.PROTOCOL_TLSv1_2)
            except FileNotFoundError:
                print("[NHC2] Certificate not found. ERROR")
                return

            self.client.tls_insecure_set(True) # TO REMOVE
            self.client.username_pw_set(user, password)
            self.client.connect(host, port, 60)
            self.client.loop_start()
            print("[NHC2] ... Set")
        except:
            print("[NHC2] client init ERROR")
            if debug is True:
                traceback.print_exc()
            return

    def __del__(self):
        print("[NHC2] ... DEL")
        self.client.disconnect()
        self.client.loop_stop()


    # Fonction appelée lors de la connexion au broker
    def __on_connect(self, client, userdata, flags, rc:mqtt.MQTTMessageInfo):
        if rc == 0:
            print("[NHC2] Connected sucess")
        else:
            print("[NHC2] Connected with result code "+str(rc))
            return

        for topic_sub in self.__topic_sub:
            self.client.subscribe(topic_sub)

        self.add_callback("hobby/control/devices/rsp",self.__callback_mng_nhc_ctrl_dev_rsp)
        self.trig_cmd_list_all()
        

    def __on_message(self, client, userdata, msg:mqtt.MQTTMessage):
        if False:
            print(f"[NHC2] Received message")
            print(f"- time : {msg.timestamp}")
            print(f"- userdata : {userdata}")
            print(f"- client : {client}")
            print(f"- payload qos : {msg.qos}")
            print(f"- payload info : {msg.info}")
            print(f"- topic {msg.topic}: {msg.payload.decode()}")
            print(f"[NHC2] End message")
        if msg.topic in self.__topic_sub_callback:
            for callback in self.__topic_sub_callback[msg.topic]:
                callback(client, userdata, msg)

    def add_callback(self, topic, callback):
        if topic not in self.__topic_sub_callback:
            self.__topic_sub_callback[topic] = []
        self.__topic_sub_callback[topic].append(callback)
    
    # Device list
    def trig_cmd_list_all(self):
        print("trig_cmd_list_all")
        topic_cmd="hobby/control/devices/cmd"
        data={"Method": "devices.list"}
        self.client.publish(topic_cmd,str(data))

    def __callback_mng_nhc_ctrl_dev_rsp(self,client, userdata, msg:mqtt.MQTTMessage):
        print("__callback_mng_nhc_ctrl_dev_rsp")
        try:
            payload = json.loads(msg.payload.decode())
            if payload["Method"] == "devices.list":
                self.__callback_mng_nhc_ctrl_dev_rsp_device_list(payload)
        except Exception as e:
            traceback.print_exc()
            print("[MQTT NHC] ERROR : __callback_mng_nhc_ctrl_dev_rsp : ",e)
        
    def __callback_mng_nhc_ctrl_dev_rsp_device_list(self,payload):
        print("================")
        print(payload)
        print("================")
        #self.__devicelist=0

    def get_device_list_info(self,uuid:str):
        tag = {}
        return 