import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from resources.lib.hs_api import hsApi
from resources.lib.kpi_name import *
class data:
    pass

class setup_function:
    def setupMethod(self,udid,AppiumUrl,session_id):
        session_data = data()
        init_timing(session_data)
        session_data.udid = udid
        session_data.AppiumUrl = AppiumUrl
        session_data.Apikey = AppiumUrl.split('/')[4]
        session_data.hs_api_call=hsApi(session_data.udid,session_data.Apikey)
        session_data.session_id = session_id
        session_data.status = "Failed"
        return session_data

    def teardownMethod(self,session_data,package,driver):
        from resources.lib import session_visual_lib
        driver.terminate_app(package)
        driver.quit()
        session_visual_lib.run_record_session_info(session_data)
        


