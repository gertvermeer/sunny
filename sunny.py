import requests
import json
import re
from flask import Flask, jsonify
from operator import itemgetter
from random import random

resp  = requests.get('https://192.168.0.150/dyn/getDashValues.json', verify=False)


app = Flask(__name__)


def return_data(input):
    dateList = re.split("-", input)
    resultDate = re.sub("T.*", "", dateList[2]) + "-" + dateList[1] + "-" + dateList[0]
    resultTime = re.sub(".*T", "", dateList[2])
    resultTime = re.sub("\..*", "", resultTime)
    resultDate = resultDate + " (" + resultTime + ")"
    return resultDate

def return_sql_date(input):
    resultDate = re.sub("T.*", "", input)
    return resultDate

@app.route('/', methods=['GET'])
def home():	
    resp  = requests.get('https://192.168.0.150/dyn/getDashValues.json', verify=False)
    json_data = resp.json()
    print json_data
    return jsonify(json_data)

@app.route('/maxtemp', methods=['GET'])
def maxtemp():
    max_url= 'http://ledmachine.local:8086/query?db=weerstats&q=SELECT max(buiten)  from temperatuur where time >= \'from_time\' and time < \'to_time\''
    resp  = requests.get('http://ledmachine.local:8086/query?db=weerstats&q=SELECT top(max,10) FROM (SELECT max(buiten) from temperatuur GROUP BY time(24h))', verify=False)
    json_data = resp.json()

    date =  json_data.get("results",{})[0].get("series")[0].get("values")[0][0]



    testdata = json_data.get("results",{})[0].get("series")[0].get("values")
    print testdata
    print "************"
    testdata = sorted(testdata, key=itemgetter(1), reverse=True)
    result = ""
    for item in testdata:
        print return_sql_date(item[0]) #  SELECT max(buiten)  from temperatuur where time >= '2020-05-09 00:00:00' and time < '2020-06-10 00:00:00'
        tempurl = re.sub("from_time",return_sql_date(item[0])+ " 00:00:00",max_url)
        tempurl = re.sub("to_time",return_sql_date(item[0])+ " 23:59:59",tempurl)
        print tempurl
        response = requests.get(tempurl).json()
        result = result + str(response.get("results",{})[0].get("series")[0].get("values")[0][1]) + " C     " +return_data(response.get("results",{})[0].get("series")[0].get("values")[0][0])  + " ;"
        print result


    return jsonify(result)



app.run(host= '0.0.0.0', port='3001')

