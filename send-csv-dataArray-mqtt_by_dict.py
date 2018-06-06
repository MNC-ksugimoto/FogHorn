#!/usr/bin/python
# root or sudo で実行（importするpahoがroot管理のため）
# append paho module path (VM : CentOS_7_301_FHEDG)
import sys
sys.path.append('/var/lib/docker/overlay2/4d546a1e6afeae2d931af1f1c851786bf3335103a491bd450a9cc5606f976c65/diff/usr/local/lib/python2.7/site-packages/')

import csv
import time
from time import sleep
import paho.mqtt.client as mqtt
import json
import time
host = '192.168.56.113' # Specify your edge id
port = 1883
topic = 'array_test_topic' #Make sure topic match to your FogHorn Edge sensor config

client = mqtt.Client(protocol=mqtt.MQTTv311)

client.connect(host, port=port, keepalive=60)

file_data = []

with open('./arraydata_jsonType.csv') as f: #Specify right path for csv file
    for line in csv.DictReader(f):
        line_json = json.dumps(line)
#        print(line_json)
        file_data.append(line_json)
#print(data)

line_data = list(file_data)
while True:
    for i in line_data:
        client.publish(topic, i)
        print(i)
        sleep(1)
