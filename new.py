#!/usr/bin/env python

import os

import requests
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict

from datetime import datetime
import time

import lcd

load_dotenv()

ace = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace'

feed = gtfs_realtime_pb2.FeedMessage()
# get response from api
response = requests.get(ace)
# pass response to parser
feed.ParseFromString(response.content)
feed = MessageToDict(feed)

from pprint import pprint
#pprint(feed)

def main():
    lcd.lcd_init()

    while True:
        timeToStation = 7
        northbound = []
        for entry in feed['entity']:
            if 'tripUpdate' in entry:
                if entry['tripUpdate']['trip']['routeId'] == 'E':
                    #pprint(entry)
                    if 'stopTimeUpdate' in entry['tripUpdate']:
                        for stopTime in entry['tripUpdate']['stopTimeUpdate']:
                            if stopTime['stopId'] in ('126', '126N', '126S', 'A25', 'A25N', 'A25S', 'B14', 'B14N', 'B14S'):
                                #pprint(stopTime)
                                #print(f"{stopTime['stopId']}:{stopTime['arrival']['time'].strftime('%Y%m%d %H:%M:%S')}")
                                timestr = stopTime['arrival']['time']
                                inttimestr = int(timestr)
                                timeToArrival = inttimestr - int(time.time())
                                humanTimeToArrival = timeToArrival // 60
                                humanTimeStr = datetime.fromtimestamp(inttimestr).strftime('%c')
                                if stopTime['stopId'][-1] == 'N':
                                    if humanTimeToArrival >= timeToStation:
                                        northbound.append(humanTimeToArrival - timeToStation)
                                #print(f"{stopTime['stopId']}:{timestr}|{humanTimeToArrival}|{humanTimeStr}")
        if northbound:
            northbound.sort()
    #        for t in northbound[:2]:
    #            print(f"{t} minutes")
            lcd.lcd_string(f"^E {northbound[0]}m", lcd.LCD_LINE_1)
            lcd.lcd_string(f"^E {northbound[1]}m", lcd.LCD_LINE_2)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd.lcd_byte(0x01, lcd.LCD_CMD)
    lcd.lcd_string("Goodbye!",lcd.LCD_LINE_1)
    lcd.GPIO.cleanup()
