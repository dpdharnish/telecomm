# python3 test_zoom.py --udid RZ8NA0Z723M --AppiumUrl https://dev-in-blr-0.headspin.io:3012/v0/150f14a11db946ffb9505e3175ae9d95/wd/hub --PlatformName android
import time
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import path
import os
import sys
import json
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from resources import action
from resources.args import Get_Args
from resources.setup import setup_function
data = Get_Args()
setup1 = setup_function()
test_name = "Zoom"
package  = "us.zoom.videomeetings"
activity = "com.zipow.videobox.LauncherActivity"
app = "Youtube"
udid,AppiumUrl,PlatformName = data.get_data()
caps = {
        "deviceName": udid,
        "udid": udid,
        "automationName": "uiautomator2",
        "appPackage": package,
        "platformName": PlatformName,
        "appActivity": activity,
        "headspin:capture":True,
        "headspin:controlLock":True
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
try:
    session_data.kpi_labels['Launch Time']['start'] = int(round(time.time() * 1000))-8000
    # Create the Appium driver
    driver.orientation = "PORTRAIT"
    wait = WebDriverWait(driver, 15)
    session_id = driver.session_id
    wait.until(EC.presence_of_element_located((MobileBy.ID,"us.zoom.videomeetings:id/zm_welcome_anim_zoom_logo")))
    session_data.kpi_labels['Launch Time']['end'] = int(round(time.time() * 1000))


    #Join meeting
    try:
        wait.until(EC.presence_of_element_located((MobileBy.ID,"us.zoom.videomeetings:id/rooted_warning_dialog_continue_btn"))).click()
    except:
        print('rootbutton not found')

    wait.until(EC.presence_of_element_located((MobileBy.ID,"us.zoom.videomeetings:id/btnJoinConf"))).click()
    # conference = driver.find_element(by=MobileBy.ID, value="us.zoom.videomeetings:id/edtConfNumber")
    session_data.kpi_labels['Join Page Load Time']['start'] = int(round(time.time() * 1000))
    conference = wait.until(EC.presence_of_element_located((MobileBy.ID,"us.zoom.videomeetings:id/edtConfNumber")))
    session_data.kpi_labels['Join Page Load Time']['end'] = int(round(time.time() * 1000))
    conference.send_keys("5578624591")
    join = driver.find_element(by=MobileBy.ID, value="us.zoom.videomeetings:id/btnJoin")
    join.click()
    time.sleep(5)
    wait.until(EC.presence_of_element_located((MobileBy.ID,"us.zoom.videomeetings:id/btnJoinWithVideo"))).click()
    print('awaiting to be let into room')
    time.sleep(5)
    wait.until(EC.presence_of_element_located((MobileBy.ID,"us.zoom.videomeetings:id/txtCallViaVoIP"))).click()




    # Timer 15 cycles of 60 seconds
    print("starting video")
    for i in range(0, 15):
        #sleep for 60 seconds
        time.sleep(60)
        print(f"{60*(i+1)} seconds passed")
        driver.find_element(MobileBy.ID,  'android:id/content')
    session_data.status = "Pass" 

except Exception as e:
    print(e)


finally:
    print('https://ui-dev.headspin.io/sessions/' + str(session_id) + '/waterfall')
    print("teardown started.....")
    setup1.teardownMethod(session_data,package,driver)  # to add kpi and tags