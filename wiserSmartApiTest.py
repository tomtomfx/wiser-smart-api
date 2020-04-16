from wiserSmartAPI import wiserSmart
import logging
import json
import time

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
    ws = wiserSmart.wiserSmart(wiserSmartIP, wiserSmartUser, wiserSmartPassword)

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

# Other Examples
# Setting HOME Mode , change to AWAY for away mode
#    wh.setHomeAwayMode("HOME")
#    wh.setHomeAwayMode("AWAY",10)
# Set room 4 TRVs to off, which is -200
#    print( wh.getRoom(4).get("Name"))
#    wh.setRoomMode(4,"off")
# Set room 4 TRVs to manual, setting normal scheduled temp
#    wh.setRoomMode(4,"manual")
# Set temperature of room 4 to 13C
#    wh.setRoomTemperature(4,10)
# Set TRV off in room 4 to Off
#    wh.setRoomTemperature(4,-20)

except json.decoder.JSONDecodeError as ex:
    print("JSON Exception")
