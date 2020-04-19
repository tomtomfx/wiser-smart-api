"""
# Wiser Smart API Facade

thomas.fayoux@gmail.com
Thanks to Angelosantagata@gmail.com who did the initial work on Drayton Wiser heating

https://github.com/tomtomfx/wiser-smart-api

This API Facade allows you to communicate with your Wiser Smart Hub.
This API is used by the homeassistant integration available at ... TBD
"""

import logging
import requests
import json
import os
import re
from base64 import b64encode

_LOGGER = logging.getLogger(__name__)

"""
Wiser Smart RPC URLS
"""
WISERSMARTDEVICELIST = "http://{}/rpc/homedevice/device_list"
WISERSMARTAPPLIANCELIST = "http://{}/rpc/loadmanagement/get_appliances"
WISERSMARTGETMODE = "http://{}/rpc/mode/get_home_mode"
WISERSMARTTEMPLIST = "http://{}/rpc/hvac/get_all_loc_temp"
WISERSMARTSETAPPLIANCESTATE = "http://{}/rpc/loadmanagement/set_appliance_state"
WISERSMARTSETMODE = "http://{}/rpc/mode/set_home_mode"
WISERSMARTSETTEMP = "http://{}/rpc/hvac/set_loc_temp"
WISERSMARTSYSTEM = "http://{}/rpc/diagnostic/get_properties"
WISERSMARTROOMS = "http://{}/rpc/devicegroup/get_groups"
WISERSMARTGETSCHEDULE = "http://{}/rpc/schedule/get_schedule"

"""
Wiser Smart modes
"""
NORMAL = "manual"
SCHEDULED = "schedule"
ENERGYSAVER = "energysaver"
HOLIDAY = "holiday"
"""
Temperatures boundaries
"""
TEMP_MINIMUM = 0.5
TEMP_MAXIMUM = 35
TEMP_OFF = -20

TIMEOUT = 5

__VERSION__ = "1.0.2"

"""
Exception Handlers
"""
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class WiserNoDevicesFound(Error):
    pass

class WiserNoRoomFound(Error):
    pass

class WiserControllerNotFound(Error):
    pass

class WiserNoHotWaterFound(Error):
    pass

class WiserRESTException(Error):
    pass

class WiserControllerDataNull(Error):
    _LOGGER.info("Wiser Smart data null after refresh")
    pass

class WiserControllerAuthenticationException(Error):
    pass

class WiserControllerTimeoutException(Error):
    pass

class wiserSmart:
    def __init__(self, wiserIP, wiserUser, wiserPassword):
        _LOGGER.info("WiserSmart API Initialised : Version {}".format(__VERSION__))
        self.wiserControllerData = None
        self.wiserHomeMode = None
        self.wiserTemperaturesData = None
        self.wiserAppliancesData = None
        self.wiserDevicesData = None
        self.wiserRoomsList = []
        self.wiserIP = wiserIP
        login = ("{}:{}".format(wiserUser, wiserPassword)).encode()
        self.auth = b64encode(login)
        print(self.auth)
        self.headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "Basic {}".format(self.auth.decode()),
        }
        print (self.headers)
        # Dict holding Radiator2Room mapping convinience variable
        self.refreshData()  # Issue first refresh in init

    def __checkTempRange(self, temp):
        """
        Validates temperatures are within the allowed range for wiser smart controller
        param temp: The temperature to check
        return: Boolean
        """
        if temp != TEMP_OFF and (temp < TEMP_MINIMUM or temp > TEMP_MAXIMUM):
            return False
        else:
            return True

    def checkControllerData(self):
        """
        Method checks the controller data object is populated, if it is not then it
        executes the refresh method, if the hubdata object is still null then
        it raises an error

        """
        if self.wiserControllerData is None:
            self.refreshData()
        if self.wiserControllerData is None:
            raise WiserControllerDataNull("Controller data null even after refresh, aborting request")
        # Otherwise continue

    def sendPostRequest(self, url, jsonData):
        """
        Generic function to send a POST request to the Wiser Controller
        """
        result = None
        try:
            resp = requests.post(
                url.format(self.wiserIP), headers=self.headers, json=jsonData, timeout=TIMEOUT
            )
            resp.raise_for_status()
            result = resp.json()
            _LOGGER.debug("Wiser Controller Data received {} ".format(self.wiserControllerData))
            
        except requests.Timeout:
            _LOGGER.debug("Connection timed out trying to update from Wiser Smart Controller")
            raise WiserControllerTimeoutException("The connection timed out.")
        except requests.HTTPError:
            if result.status_code == 401:
                raise WiserControllerAuthenticationException(
                    "Authentication error.  Check user & password."
                )
            elif result.status_code == 404:
                raise WiserRESTException("Not Found.")
            else:
                raise WiserRESTException("Unknown Error.")
        except requests.ConnectionError:
            _LOGGER.debug("Connection error trying to update from Wiser Controller")
            raise WiserControllerNotFound("Wiser Controller data update failed")
        
        return result

    def refreshData(self):
        """
        Forces a refresh of data from the wiser Controller
        return: JSON Data
        """

        _LOGGER.info("Updating Wiser Smart Controller Data")
        emptyBody = {}
        
        # System data
        systemData = {"propertyNames":["ehc.gw.host.name","ehc.wcs2.cloud.status","ehc.version.macaddress"]}        
        self.wiserControllerData = self.sendPostRequest(WISERSMARTSYSTEM, systemData)

        # Get home mode
        self.wiserHomeMode = self.sendPostRequest(WISERSMARTGETMODE, emptyBody)

        # Get rooms
        roomsInfos = self.sendPostRequest(WISERSMARTROOMS, emptyBody)
        for room in roomsInfos.get("groupDetails"):
            if room.get("visible") == True:
                self.wiserRoomsList.append(room.get("name"))

        # Get devices
        self.wiserDevicesData = self.sendPostRequest(WISERSMARTDEVICELIST, emptyBody)

        # Get Temperatures
        self.wiserTemperaturesData = self.sendPostRequest(WISERSMARTTEMPLIST, emptyBody)

        # Get appliances
        self.wiserAppliancesData = self.sendPostRequest(WISERSMARTAPPLIANCELIST, emptyBody)
        
    def getWiserControllerName(self):
        self.checkControllerData()
        for prop in self.wiserControllerData.get("propertyDetails"):
            if prop.get("name") == "ehc.gw.host.name":
                return prop.get("value")

    def getWiserControllerCloudConnection(self):
        self.checkControllerData()
        for prop in self.wiserControllerData.get("propertyDetails"):
            if prop.get("name") == "ehc.wcs2.cloud.status":
                return prop.get("value")

    def getWiserHomeMode(self):
        self.checkControllerData() # trigger a data refresh if necessary
        return self.wiserHomeMode.get("homeMode")

    def setWiserHomeMode(self, hcMode, homeMode, comeBackTime):
        self.checkControllerData() # trigger a data refresh if necessary
        antiFreeze = False
        if (homeMode == "holiday"): 
            antiFreeze = True
        homeModeData = {"hcMode":hcMode,"homeMode":homeMode,"antiFreeze":antiFreeze,"endTime":comeBackTime}
        self.sendPostRequest(WISERSMARTSETMODE, homeModeData)

    def getWiserRooms(self):
        self.checkControllerData() # trigger a data refresh if necessary
        return self.wiserRoomsList

    def getWiserRoomInfo(self, roomName):
        self.checkControllerData() # trigger a data refresh if necessary
        for roomTemp in self.wiserTemperaturesData.get("locationTempDetails"):
            if roomTemp.get("locationName") == roomName:
                return roomTemp
        return None
    
    def setWiserRoomTemp(self, roomName, temp):
        self.checkControllerData() # trigger a data refresh if necessary
        # Check temp is between boundaries
        if (temp < TEMP_MINIMUM):
            temp = TEMP_MINIMUM
        if (temp > TEMP_MAXIMUM):
            temp = TEMP_MAXIMUM
        roomData = {"targetTemp":[{"locationId":roomName,"targetValue":temp}]}
        self.sendPostRequest(WISERSMARTSETTEMP, roomData)

    def getWiserDevices(self):
        self.checkControllerData() # trigger a data refresh if necessary
        return self.wiserDevicesData.get("device")
    
    def getWiserDeviceInfo(self, deviceName):
        self.checkControllerData() # trigger a data refresh if necessary
        for device in self.wiserDevicesData.get("device"):
            if device.get("name") == deviceName:
                return device
        return None

    def getWiserAppliances(self):
        self.checkControllerData() # trigger a data refresh if necessary
        return self.wiserAppliancesData.get("applianceDetails")

    def getWiserApplianceInfo(self, applianceName):
        self.checkControllerData() # trigger a data refresh if necessary
        for appliance in self.wiserAppliancesData.get("applianceDetails"):
            if appliance.get("applianceName") == applianceName:
                return appliance
        return None

    def setWiserApplianceState(self, applianceName, state):
        self.checkControllerData() # trigger a data refresh if necessary
        for appliance in self.wiserAppliancesData.get("applianceDetails"):
            if appliance.get("applianceName") == applianceName:
                applianceData = {"applianceState":[{"applianceId":appliance.get("applianceId"), "state":state}]}
                self.sendPostRequest(WISERSMARTSETAPPLIANCESTATE, applianceData)
