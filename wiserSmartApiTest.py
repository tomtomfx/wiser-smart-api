from wiserSmartAPI.wiserSmart import wiserSmart
import logging
import json
import time
import datetime

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# Get Wiser Parameters from keyfile
with open("wisersmart.params", "r") as f:
    data = f.read().split("\n")
wiserkey = ""
wiserip = ""

# Get wiserSmart local infos from wiserSmart.params file
# This file is not source controlled as it contains the testers secret etc

for lines in data:
    line = lines.split("=")
    if line[0] == "wiserSmartIP":
        wiserSmartIP = line[1]
    if line[0] == "wiserSmartUser":
        wiserSmartUser = line[1]
    if line[0] == "wiserSmartPassword":
        wiserSmartPassword = line[1]

print("Wiser Smart IP: {} , Wiser Smart User: {}, Wiser Smart Password: {}".format(wiserSmartIP, wiserSmartUser, wiserSmartPassword))


try:
    ws = wiserSmart(wiserSmartIP, wiserSmartUser, wiserSmartPassword)

    print("-------------------------------")
    print("System status")
    print("-------------------------------")
    print ("Wiser Controller Name: {}".format(ws.getWiserControllerName()))
    print ("Cloud connection status: {}".format(ws.getWiserControllerCloudConnection()))
    print ("Wiser smart Home Mode: {}".format(ws.getWiserHomeMode()))
    
    print("--------------------------------")
    print("List of Devices")
    print("--------------------------------")
    for device in ws.getWiserDevices():
        print(device.get("name"))
        print("\tModel: {}".format(device.get("modelId")))
        print("\tRoom: {}".format(device.get("location")))
        print("\tStatus: {}".format(device.get("status")))
        print("\tPower type: {}".format(device.get("powerType")))
        if (device.get("powerType") == "Battery"):
            print("\tBattery level: {}".format(device.get("batteryLevel")))
    print("--------------------------------")
    print("Listing all Rooms and their temperature")
    print("--------------------------------")
    roomList = ws.getWiserRooms()
    print ("There are {} rooms in the house".format(len(roomList)))
    for room in roomList:
        print(room)
        temperatures = ws.getWiserRoomInfo(room)
        if(temperatures != None):
            print("\tCurrent temp: {}".format(temperatures.get("currentValue")))
            print("\tTarget temp: {}".format(temperatures.get("targetValue")))
    print("--------------------------------")
    print("Listing all smartplugs")
    print("--------------------------------")
    for appliance in ws.getWiserAppliances():
        print(appliance.get("applianceName"))
        print("\tActive: {}".format(appliance.get("state")))
        print("\tPower consumption: {}".format(appliance.get("powerConsump")))

# Set Machine à laver off
    print("--------------------------------")
    print("Set data tests")
    print("--------------------------------")
    
    # print('Set "Machines à laver" off')
    # ws.setWiserApplianceState("Machines à laver", False)
    
    # time.sleep(5)
    
    # print('Set mode') # manual, schedule, energysaver, holiday
    #comeBackTime = int(datetime.datetime(2020,4,18,15,0).timestamp())
    # comeBackTime = None
    # ws.setWiserHomeMode("schedule", "schedule", comeBackTime)
    
    # time.sleep(5)
    
    # print('Room Temp')
    # ws.setWiserRoomTemp("Chambre bas", 11.3)
    
except json.decoder.JSONDecodeError as ex:
    print("JSON Exception")
