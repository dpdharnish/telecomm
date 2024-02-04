# command = python3 test_cod.py --udid RFCRC08KCAX --AppiumUrl https://dev-in-blr-0.headspin.io:3012/v0/150f14a11db946ffb9505e3175ae9d95/wd/hub --PlatformName android
import time
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import path
import os
import sys
import json
import argparse
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from resources import action
from resources.args import Get_Args
from resources.setup import setup_function
setup1 = setup_function()
data = Get_Args()
test_name = "Call Of Duty"
package  = "com.activision.callofduty.shooter"
activity = "com.tencent.tmgp.cod.CODMainActivity"
udid,AppiumUrl,PlatformName = data.get_data()
caps = {
        "deviceName": udid,
        "udid": udid,
        "automationName": "uiautomator2",
        "appPackage": package,
        "platformName": PlatformName,
        "appActivity": activity,
        "headspin:capture":True,
        "headspin:controlLock":True,
        "headspin:capture.network":False
    }


# Create driver
try:
    driver = webdriver.Remote(AppiumUrl, caps)
except Exception as e:
    print("error starting driver.  Stacktrace:")
    print(f"{e}")
    sys.exit(-1)
session_id = driver.session_id
session_data = setup1.setupMethod(udid,AppiumUrl,session_id)  #setup method
session_data.test_name = test_name
session_data.package = package
session_data.activity = activity
wait = WebDriverWait(driver, 15)
# driver.orientation = "PORTRAIT"


try:
    wait = WebDriverWait(driver, 300)
    session_data.kpi_labels['Launch Time']['start'] = int(round(time.time() * 1000))-8000
    wait.until(EC.presence_of_element_located((MobileBy.ID, 'android:id/content')))
    session_data.kpi_labels['Launch Time']['end'] = int(round(time.time() * 1000))
    #Find & Open COD from settings app
    # Wait 2 minutes to download resources 
    wait.until(EC.presence_of_element_located((MobileBy.ID, 'com.google.android.gms:id/account_display_name'))).click()
    


    time.sleep(15)
    #Click [X] in pop up menu
    for i in range(3):
        action.tap(driver,1760,194)
        action.tap(driver,1780,164)
        action.tap(driver,1751,166)


    #Tap Multiplayer
    action.tap(driver,2022,484)


    ## REQUIRES USER INPUT
    for i in range(30):
        print('need user input')
        time.sleep(1)

    for i in range (5):
        action.move_forward(driver)
        action.move_forward(driver)
        action.move_forward(driver)
        action.move_forward(driver)
        action.move_forward(driver)
        action.move_forward(driver)
        action.look_left(driver)
        action.move_forward(driver)
        action.look_right(driver)
        action.look_right(driver)
        action.look_right(driver)
        action.move_forward(driver)
        time.sleep(1)
    session_data.status = "Pass"

except Exception as e:
    print(e)

finally:
    print('https://ui-dev.headspin.io/sessions/' + str(session_id) + '/waterfall')
    print("teardown started.....")
    setup1.teardownMethod(session_data,package,driver)