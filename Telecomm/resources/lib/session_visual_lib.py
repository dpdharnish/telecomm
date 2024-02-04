# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import json

from resources.lib.hs_api import hsApi
import time
from resources.lib.hs_logger import logger


def run_record_session_info(self):
    '''
    Save KPI and Description to session
    '''
    logger.info('run_record_session_info')
    run_add_annotation_data(self)
    run_add_session_data(self)
    logger.info("https://ui-dev.headspin.io/sessions/" +
                str(self.session_id)+"/waterfall")


def run_add_session_data(self):
    '''
    Save KPI Label info to description 
    '''
    logger.info("run add session data")

    session_data = get_general_session_data(self)

    result = self.hs_api_call.add_session_data(session_data)
    logger.info('result')
    logger.info(result)
    
    description_string = ""
    for data in session_data['data']:
        description_string += data['key'] + " : " + str(data['value']) + "\n"

    #API call for adding session description
    self.hs_api_call.update_session_name_and_description(
        self.session_id, self.test_name, description_string)

    #for adding tags to session.
    self.hs_api_call.add_session_tags(self.session_id, tags= self.tags)

def get_general_session_data(self):
    #In this function we are creating session data dict for post processing
    '''
    General Session Data, include phone os, phone version ....
    '''
    session_status = None
    if self.status != "Pass":
        session_status = "Failed"
    else:
        session_status = "Passed"

    session_data = {}
    session_data['session_id'] = self.session_id
    session_data['test_name'] = self.test_name
    session_data['status'] = session_status
    session_data['data'] = []
    # app info
    session_data['data'].append(
        {"key": 'bundle_id', "value": self.package})
    session_data['data'].append({"key": 'status', "value": self.status})

    #add the non duration kpi to session data
    if self.non_time_kpis:
        for key,value in self.non_time_kpis.items():
            if not ((key == "video_first_frame_play_time") and (value is None)):
                print (key,value)
                session_data['data'].append(
                    {"key": key, "value": value})
                
    session_data = add_kpi_data_from_labels(self, session_data)

    try:
        session_data['data'].append(
            {"key": 'fail_reason', "value": self.status})
    except:
        pass

    return session_data


def get_video_start_timestamp(self):
    logger.info('get_video_start_timestamp')
    wait_until_capture_complete = True
    t_end = time.time()+600
    if wait_until_capture_complete:
        while time.time() < t_end:
            capture_timestamp = self.hs_api_call.get_capture_timestamp(
                self.session_id)
            logger.info(capture_timestamp)
            self.video_start_timestamp = capture_timestamp['capture-started'] * 1000
            if 'capture-complete' in capture_timestamp:
                break
            time.sleep(1)
    else:
        capture_timestamp = self.hs_api_call.get_capture_timestamp(
            self.session_id)
        self.video_start_timestamp = capture_timestamp['capture-started'] * 1000


def run_add_annotation_data(self):
    '''
    Add annotation from kpi_labels
    '''
    logger.info("run add annotation to session")
    get_video_start_timestamp(self)
    wait_for_session_video_becomes_available(self)
    add_kpi_labels(self, self.kpi_labels, self.KPI_LABEL_CATEGORY)

def wait_for_session_video_becomes_available(self):
    t_end = time.time() + 600
    while time.time() < t_end:
        status = self.hs_api_call.get_session_video_metadata(self.session_id)
        if status and ("video_duration_ms" in status):
            logger.info(str(status))
            break
        logger.info("Waiting for session video becomes available")
        


def add_kpi_data_from_labels(self, session_data):
    '''
    Merge kpi labels and interval time
    '''
    for label_key in self.kpi_labels.keys():
        if self.kpi_labels[label_key] and 'start' in self.kpi_labels[label_key] and 'end' in self.kpi_labels[label_key]:
            data = {}
            data['key'] = label_key
            start_time = self.kpi_labels[label_key]['start']
            end_time = self.kpi_labels[label_key]['end']
            if start_time and end_time:
                data['value'] = end_time - start_time
                session_data['data'].append(data)
    return session_data


def get_screenchange_list_divide(self, label_key, label_start_time, label_end_time,
                                 start_sensitivity=None, end_sensitivity=None, video_box=None):
    """
        Given a visual page load of the region
        If there are start and end, there is only 1 region in the middle that might have more screen changes.
        If start and end are the same we are done
    """
    screen_change_list = []
    sn = 0
    sn_limit = 10
    segment_time_step = 100
    try:
        segment_time_step = self.segment_time_step
    except AttributeError:
        pass
    pageload = self.hs_api_call.get_pageloadtime(self.session_id, str(label_key) + str(sn), label_start_time, label_end_time,
                                                 start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity, video_box=video_box)
    logger.debug(pageload)
    if 'page_load_regions' in list(pageload.keys()) and 'message' not in pageload['page_load_regions']:
        while True:
            screen_change_list.append(
                pageload['page_load_regions'][0]['start_time'])
            screen_change_list.append(
                pageload['page_load_regions'][0]['end_time'])
            sn += 1
            if sn_limit < sn:
                break
            new_label_start_time = float(
                pageload['page_load_regions'][0]['start_time']) + segment_time_step
            new_label_end_time = float(
                pageload['page_load_regions'][0]['end_time']) - segment_time_step
            if new_label_start_time > new_label_end_time:
                break
            logger.debug('new_label_start_time:' + str(new_label_start_time))
            logger.debug('new_label_end_time:' + str(new_label_end_time))
            pageload = self.hs_api_call.get_pageloadtime(self.session_id, str(label_key) + str(sn), new_label_start_time, new_label_end_time,
                                                         start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity)
            if 'page_load_regions' not in list(pageload.keys()) or 'error_msg' in pageload['page_load_regions'][0]:
                logger.debug(pageload)
                if 'status' in pageload:
                    # Prevent bad data to get into the database
                    # self.status = 'Page Load Error'
                    pass
                break
    else:
        # Prevent bad data to get into the database
        # self.status = 'Page Load Error'
        pass
        logger.debug(pageload)

    screen_change_list = sorted(list(set(screen_change_list)))
    logger.info(label_key + str(screen_change_list))
    print((label_key + ' ' + str(screen_change_list)))
    return screen_change_list


def add_kpi_labels(self, labels, label_category):
    '''
        Find all the screen change using different increments
        From the screen changes, pick the desired region
        1. Make sure we can produce the regions that we want to work with 100%
        2. Pick the regions in the code to be inserted for labels kpi

        If there is segment_start and segment_end, find all the candidate regions, and use segment_start and segment_end to pick
        segment_start 
        segment_end 
        0 => Pick the first segment from the start
        1 => Pick the second segmenet from the start
        -1 => Pick the last segment from the end
        -2 => Pick the second to last segmene from the end
    '''
    logger.info("add_kpi_labels")
    print(labels)
    for label_key in labels.keys():
        label = labels[label_key]
        logger.debug(label)
        if label['start'] and label['end']:
            label_start_time = label['start'] - self.video_start_timestamp
            if(label_start_time < 0):
                label_start_time = 0.0
            label_end_time = label['end'] - self.video_start_timestamp

            logger.info("Add Desired Region " + str(label_key) +
                        " "+str(label_start_time)+" "+str(label_end_time))
            self.hs_api_call.add_label(
                self.session_id, label_key, 'desired region', (label_start_time)/1000, (label_end_time)/1000)

            start_sensitivity = None
            end_sensitivity = None
            video_box = None
            if 'start_sensitivity' in label:
                start_sensitivity = label['start_sensitivity']
            if 'end_sensitivity' in label:
                end_sensitivity = label['end_sensitivity']
            if 'video_box' in label:
                video_box = label['video_box']
                
            new_label_start_time = None
            new_label_end_time = None

            if 'segment_start' in labels[label_key] and 'segment_end' in labels[label_key]:
                # Get candidate screen change list, example [2960, 4360, 8040, 9480, 9960, 11560, 13560, 13800, 17720, 18040]
                screen_change_list = get_screenchange_list_divide(
                    self, label_key, label_start_time, label_end_time, start_sensitivity, end_sensitivity, video_box)
                try:
                    if screen_change_list:
                        new_label_start_time = float(
                            screen_change_list[labels[label_key]['segment_start']])
                        new_label_end_time = float(
                            screen_change_list[labels[label_key]['segment_end']])
                            
                except:
                    # self.status = 'Page Load Segement Error'
                    pass
            else:
                if label['start'] and label['end']:
                    pageload = self.hs_api_call.get_pageloadtime(
                        self.session_id, label_key, label_start_time, label_end_time, start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity)
                    if 'page_load_regions' in list(pageload.keys()) and 'error_msg' not in pageload['page_load_regions'][0]:
                        new_label_start_time = float(
                            pageload['page_load_regions'][0]['start_time'])
                        new_label_end_time = float(
                            pageload['page_load_regions'][0]['end_time'])
                    print(new_label_start_time, new_label_end_time)
            if new_label_start_time and new_label_end_time:
                self.kpi_labels[label_key]['start'] = new_label_start_time
                self.kpi_labels[label_key]['end'] = new_label_end_time

                # validate kpi = 0
                kpi_value = self.kpi_labels[label_key]['end'] - \
                    self.kpi_labels[label_key]['start']

                if int(kpi_value) == 0:
                    self.kpi_labels[label_key]['start'] = self.kpi_labels[label_key]['start'] - 200
                    self.kpi_labels[label_key]['end'] = self.kpi_labels[label_key]['end'] + 200
                print(self.session_id, label_key, label_category, (new_label_start_time)/1000, (new_label_end_time)/1000)
                self.hs_api_call.add_label(self.session_id, label_key, label_category, (
                    new_label_start_time)/1000, (new_label_end_time)/1000)
                logger.info("label added")
        else:
            logger.debug('Label not found for:' +
                         str(label_key) + ' ' + label_category)
