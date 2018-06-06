# coding: utf-8
#!/usr/bin/python

import sys
# append paho module path (Dell Embedded PC3000)
sys.path.append('/var/lib/docker/overlay2/790fca0c2afa2451eccc315468e4dfdcd69f288359858687dc046ff8da747595/diff/usr/local/lib/python2.7/site-packages/')

import pandas as pd
import csv
import time
from time import sleep
import paho.mqtt.client as mqtt
import json
import time
host = '172.26.24.188' # Specify your edge id
port = 1883
topic = 'infer_result-AST1' #Make sure topic match to your FogHorn Edge sensor config

client = mqtt.Client(protocol=mqtt.MQTTv311)

client.connect(host, port=port, keepalive=60)



df = pd.read_csv("./AST.csv")

# ヘッダーがある場合
json_str = df.to_json(orient="records")
#print(type(json_str))

# json形式の辞書型変換
list_vals = json.loads(json_str)
#print(type(list_vals))

# list形式に変換
lines_data = list(list_vals)
while True:
    for line in lines_data:
    	# jsonエンコード
        line_json = json.dumps(line)
        client.publish(topic, line_json)
        print(line_json)
        sleep(2)
