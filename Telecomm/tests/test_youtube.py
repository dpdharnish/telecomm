# Search python3 test_youtube.py --udid RZ8NA0Z723M --AppiumUrl https://dev-in-blr-0.headspin.io:3012/v0/150f14a11db946ffb9505e3175ae9d95/wd/hub --PlatformName android
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
test_name = "youtube"
package  = "com.google.android.youtube"
activity = "com.google.android.apps.youtube.app.watchwhile.WatchWhileActivity"
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
wait = WebDriverWait(driver, 15)
driver.orientation = "PORTRAIT"


try:
    session_data.kpi_labels['Launch Time']['start'] = int(round(time.time() * 1000))-10000
    wait.until(EC.presence_of_element_located((MobileBy.XPATH, '//android.widget.ImageView[@content-desc="Search"]')))
    session_data.kpi_labels['Launch Time']['end'] = int(round(time.time() * 1000))
    time.sleep(3)
    session_data.kpi_labels['Search Tab Load Time']['start'] = int(round(time.time() * 1000))
    wait.until(EC.presence_of_element_located((MobileBy.XPATH, '//android.widget.ImageView[@content-desc="Search"]'))).click()
    wait.until(EC.presence_of_element_located((MobileBy.ID, 'com.google.android.youtube:id/search_edit_text')))
    session_data.kpi_labels['Search Tab Load Time']['end'] = int(round(time.time() * 1000))
    wait.until(EC.presence_of_element_located((MobileBy.ID, 'com.google.android.youtube:id/search_edit_text'))).send_keys("ABC Live")
    driver.press_keycode(66)
    session_data.kpi_labels['Search Time']['start'] = int(round(time.time() * 1000))
    wait.until(EC.presence_of_element_located((MobileBy.XPATH, '(//android.view.ViewGroup)[5]')))
    session_data.kpi_labels['Search Time']['end'] = int(round(time.time() * 1000))
    time.sleep(2)
    # driver.find_element(MobileBy.ACCESSIBILITY_ID,'Latest from ABC News')
    action.tap(driver, 355, 527)
    action.tap(driver,514, 543)
    time.sleep(1)
    driver.orientation = "LANDSCAPE"
    #
    # Timer 15 cycles of 60 seconds
    print("starting video")
    for i in range(0, 15):
        #sleep for 60 seconds
        time.sleep(5)
        print(f"{5*(i+1)} seconds passed")
        driver.find_element(MobileBy.ID,  'android:id/content')
    session_data.status = "Pass"
except Exception as e:
    print(e)
    sys.exit(-1)

finally:
    print('https://ui-dev.headspin.io/sessions/' + str(session_id) + '/waterfall')
    print("teardown started.....")
    setup1.teardownMethod(session_data,package,driver)



