from __future__ import absolute_import
from __future__ import print_function
from time import sleep
import subprocess
import shlex
import os
import requests
import json
import traceback

DEFAULT_TIMEOUT = 240
LONG_TIMOUT = 4 * 60


class hsApi:
    # API for getting all devices and its details present in  an org
    device_list_url = "https://api-dev.headspin.io/v0/devices"
    get_auto_config = "https://api-dev.headspin.io/v0/devices/automation-config"
    url_root = "https://api-dev.headspin.io/v0/"
    # API for getting all devices and its details present in  an org

    def __init__(self, UDID, access_token):
        self.UDID = UDID
        self.access_token = access_token
        self.headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        # Get the deivce details
        r = requests.get(self.device_list_url, headers=self.headers)
        self.device_list_resp = self.parse_response(r)
        r = r.json()
        
        self.devices = r['devices']
        is_desired_device = False
        for device in self.devices:
            self.device_os = device['device_type']
            if self.device_os == "android" and device['serial'] == self.UDID:
                is_desired_device = True
            if self.device_os == "ios" and device['device_id'] == self.UDID:
                is_desired_device = True
            if is_desired_device:
                self.device_details = device
                self.device_hostname = device['hostname']
                self.device_address = "{}@{}".format(
                    self.UDID, self.device_hostname)
                self.device_os = device['device_type']
                break

#		current_file_dir = os.path.dirname(os.path.abspath(__file__))
#		setup_folder = os.path.abspath(os.path.join(current_file_dir, '..'))
#		print "Path to set up folder",setup_folder
#		device_details = setup_folder+"/device_details.json"
#
#		with open(device_details, 'w') as f:
#			json.dump(r, f)

#		return devices

    def parse_response(self, response):
        try:
            if response.ok:
                # print(response.content)
                try:
                    return response.json()
                except:
                    return response.text
            else:
                print((response.status_code))
                print('something went wrong')
                print((response.text))
        except:
            print((traceback.print_exc()))

    def add_session_tags(self, session_id, tags):
        #for adding kpi as tags to sessions 
        # session_data  will be 
        # [{'key': 'bundle_id', 'value': 'com.vzw.hss.myverizo'},{......}   format
        api_endpoint = "https://api-dev.headspin.io/v0/sessions/tags/{}".format(
            session_id)
        # pay_load = []
        # for data in session_data:
        #      pay_load.append({"%s" % data['key']: data['value']})
        # key = 'connection_status'
        # value = tags[0]['value']
        # pay_load = []
        # pay_load.append({"%s" % key: value})
        r = requests.post(url=api_endpoint, json=tags, headers={
                          'Authorization': 'Bearer {}'.format(self.access_token)})
        print(r)
        print(r.text)
          

    # Add data to existing session
    def add_session_data(self, session_data):
        # Expecting the input dictionary as the argument
        # Sample
        # {"session_id": "<session_id>", "test_name": "<test_name>", "data":[{"key":"bundle_id","value":"com.example.android"}] }
        request_url = self.url_root + "perftests/upload"
        response = requests.post(
            request_url, headers=self.headers, json=session_data, timeout=DEFAULT_TIMEOUT)
        return self.parse_response(response)

    def update_session_name_and_description(self, session_id, name, description):
        request_url = self.url_root + 'sessions/' + session_id + '/description'
        data_payload = {}
        data_payload['name'] = name
        data_payload['description'] = description
        print(request_url)
        print(data_payload)
        response = requests.post(
            request_url, headers=self.headers, json=data_payload, timeout=DEFAULT_TIMEOUT)
        return self.parse_response(response)

    def get_capture_timestamp(self, session_id):
        request_url = self.url_root + 'sessions/' + session_id+'/timestamps'
        response = requests.get(request_url, headers=self.headers)
        response.raise_for_status()
        # print self.parse_response(response)
        return self.parse_response(response)

    def add_label(self, session_id, name, category, start_time, end_time, pinned=False, label_type='user', data=None):
        '''
        add annotations to session_id with name, category, start_time, end_time
        '''
        request_url = self.url_root + 'sessions/' + session_id + '/label/add'
        data_payload = {}
        data_payload['name'] = name
        data_payload['category'] = category
        data_payload['start_time'] = str(start_time)
        data_payload['end_time'] = str(end_time)
        data_payload['data'] = data
        data_payload['pinned'] = pinned
        data_payload['label_type'] = label_type
        response = requests.post(
            request_url, headers=self.headers, json=data_payload)
        response.raise_for_status()
        return self.parse_response(response)

    # Get the session video metadata
    def get_session_video_metadata(self, session_id):
        request_url = f"https://api-dev.headspin.io/v0/sessions/{session_id}/video/metadata"
        response = requests.get(
                request_url, headers=self.headers)
        return response.json()
    
    def run_adb_command(self,  commmand_to_run):
        api_endpoint = "https://api-dev.headspin.io/v0/adb/{}/shell".format(
            self.UDID)
        r = requests.post(url=api_endpoint, data=commmand_to_run,
                          headers=self.headers, timeout=120)
        print(r)
        result = r.json()
        print(result)
        stdout = result['stdout'].encode('utf-8').strip()
        return stdout

    def get_pageloadtime(self, session_id, name, start_time, end_time, start_sensitivity=None, end_sensitivity=None, video_box=None):
        request_url = self.url_root + 'sessions/analysis/pageloadtime/'+session_id
        data_payload = {}
        region_times = []
        start_end = {}
        start_end['start_time'] = str(start_time/1000)
        start_end['end_time'] = str(end_time/1000)
        start_end['name'] = name
        region_times.append(start_end)
        data_payload['regions'] = region_times
        if(start_sensitivity is not None):
            data_payload['start_sensitivity'] = start_sensitivity
        if(end_sensitivity is not None):
            data_payload['end_sensitivity'] = end_sensitivity
        if(video_box is not None):
            data_payload['video_box'] = video_box

        response = requests.post(
            request_url, headers=self.headers, json=data_payload)
        response.raise_for_status()
        results = self.parse_response(response)
        return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--udid', '--udid', dest='udid',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="udid")
    parser.add_argument('--access_token', '--access_token', dest='access_token',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="access_token")
    
    args = parser.parse_args()
    udid = args.udid
    access_token = args.access_token
    hs_api = hsApi(udid, access_token)
    
    with open('data.txt', 'w') as outfile:
        json.dump(hs_api.device_list_resp, outfile)
