import os
import inspect
import requests
import sys
from datetime import datetime
from datetime import timedelta
from Site24Module.site24configuration import Configuration

# 24x7 API reference doc: https://www.site24x7.com/help/api/index.html#authentication
# go to above link, follow directions to create a code for yourself.
# Scope used to get 'code' parameter depends on action. For monitor list use Site24x7.Admin.Read
# for maintenance post, use Site24x7.Operations.Create
# these scope codes have to be created every time you make a NEW application script. Otherwise, you should be fine to use it the first time and get the refresh token (coded in below)
# put client ID & secret in config.yaml as well as the newly created scope code
## TODO: add function to pull BU information instead of hardcode
## TODO: make class variables private & use @property

class Site24x7OAuth:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_url = "https://accounts.zoho.com/oauth/v2/"
        basedir = os.path.dirname(inspect.getfile(Configuration))
        config = Configuration(os.path.join(basedir, 'site24config.yaml'))
        #These 2 are necessary for operation
        #******************************************************************
        self.ops_refresh_token = config.get_all_ops_read_refresh_token()
        #******************************************************************
        #These 2 may be needed if more business units are added, but are not currently in use
        #******************************************************************
        # self.msp_read_refresh_token = config.get_msp_read_refresh_token()
        # self.bu_read_refresh_token = config.get_bu_read_refresh_token()
        #******************************************************************
        #self.account_read_refresh_token = config.get_account_read_refresh_token()

        ops_tokens = self.get_acc_from_refresh(self.ops_refresh_token)["access_token"] #this refresh is for 'Site24x7.Account.READ Site24x7.admin.READ Site24x7.operations.CREATE'
        self.opp_acc_token = ops_tokens
        

    def get_tokens(self, code):
        api_url = self.api_url + "token"
        response = requests.post(api_url, headers={"Accept":"application/json; version=2.0"},
                         params={"client_id":self.client_id,
                                 "client_secret": self.client_secret,
                                 "code": code, #this comes from generating on website
                                 "grant_type":"authorization_code"})
        return response.json()
    
    def get_server_tokens(self, scope):
        params = {"client_id":self.client_id,
                  "response_type":"code",
                  "redirect_uri":"10.160.4.30/maint",
                  "scope":scope,
                  "access_type":"offline",
                  "prompt":"consent"}
        api_url = self.api_url + "auth"
        response = requests.get(api_url, headers={"Accept":"application/json; version=2.0"}, params=params)
        #print(response)
        return response.json()

    def get_acc_from_refresh(self, refresh_token):
        # uses refresh token from file if it exists and returns acc token
        api_url = self.api_url + "token"
        response = requests.post(api_url, headers={"Accept":"application/json; version=2.0"},
                         params={"client_id":self.client_id,
                                 "client_secret": self.client_secret,
                                 "refresh_token": refresh_token, #this comes from generating on website
                                 "grant_type":"refresh_token"})
        #print(response.json())
        return response.json()

class Site24x7:

    def __init__(self):
        self.api_url = "https://www.site24x7.com/api"
        basedir = os.path.dirname(inspect.getfile(Configuration))
        config = Configuration(os.path.join(basedir, 'site24config.yaml'))
        client_details = config.get_client_details()
        self.authorization = Site24x7OAuth(client_details["client_id"], client_details["client_secret"])

    def get_monitor_id(self, name, business_unit):
        headers = {
            "Accept": "application/json; version = 2.1",
            "Authorization" : "Zoho-oauthtoken " + self.authorization.opp_acc_token,
            "Cookie" : "zaaid=" + str(business_unit)
        }

        response = requests.get(f'https://www.site24x7.com/api/monitors/name/{name}', headers = headers).json()
        if "data" in response:
            return response["data"]["monitor_id"]
        else:
            print("Monitor", name, "not found. Please check spelling or place in maintenance manually")
            #should add fails to a file
            return None

    def get_all_monitors(self, business_unit):
        headers = {
            "Accept": "application/json; version = 2.0",
            "Authorization" : "Zoho-oauthtoken " + self.authorization.opp_acc_token,
            "Cookie" : "zaaid=" + str(business_unit)
        }
        response = requests.get(f'https://www.site24x7.com/api/monitors', headers = headers).json()
        #print(response)
        return response["data"]

    def get_all_user_groups(self, business_unit):
        headers = {
            "Accept": "application/json; version = 2.0",
            "Authorization" : "Zoho-oauthtoken " + self.authorization.opp_acc_token,
            "Cookie" : "zaaid=" + str(business_unit)
        }
        response = requests.get(f'https://www.site24x7.com/api/user_groups', headers = headers).json()
        return response["data"]

    def get_all_users(self, business_unit):
        headers = {
            "Accept": "application/json; version = 2.0",
            "Authorization" : "Zoho-oauthtoken " + self.authorization.opp_acc_token,
            "Cookie" : "zaaid=" + str(business_unit)
        }
        response = requests.get(f'https://www.site24x7.com/api/users', headers = headers).json()
        return response["data"]

    def sort_by_BU(self, maintenance_list):
        #sort the list by BU and post them (BU is at index 5)
        # maintenance_list is ([hostname, monitor_id, startdate, starttime, duration, businessunit])
        bu_sort = sorted(maintenance_list, key = lambda x: x[5])
        return bu_sort

    def handle_maintenance_list(self, maintenance_list, username):
        sorted_ls = self.sort_by_BU(maintenance_list)
        #print(sorted_ls, flush=True)

        sublist = []
        prev = sorted_ls[0][5]

        for entry in sorted_ls:
            if entry[5] == prev:
                sublist.append(entry)
            else:
                self.post_maintenance(sublist, username)
                sublist = [entry]

        self.post_maintenance(sublist, username)

    #     # self.post_maintenance(acc_token, maintenance_sublist, business_unit)

    def post_maintenance(self, maintenance_list, username):
        #convert times from string into datetime obj so we can find end date and time
        #print(maintenance_list, flush=True)
        # maintenance_list is ([hostname, monitor_id, startdate, starttime, duration, businessunit])

        start_date = maintenance_list[0][2]
        start_time = maintenance_list[0][3]
        date_time = datetime.combine(start_date, start_time)
        duration = timedelta(minutes=int(maintenance_list[0][4]))
        end_datetime = date_time + duration

        #convert times back to string for posting the maint
        start_date = start_date.strftime("%Y-%m-%d")
        start_time = start_time.strftime("%H:%M")
        end_date = end_datetime.strftime("%Y-%m-%d")
        end_time = end_datetime.strftime("%H:%M")

        id_list = [host[1] for host in maintenance_list]

        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json; version=2.0',
            'Authorization': 'Zoho-oauthtoken ' + self.authorization.opp_acc_token,
            'Cookie': 'zaaid=' + str(maintenance_list[0][5]),
        }

        data = {
            "maintenance_type": 3,
            "selection_type": 2,
            "start_time": start_time,
            "end_time": end_time,
            "display_name": "CRC Tool Generated Maintenance by " + username,
            "monitors": id_list,
            "start_date": start_date,
            "end_date": end_date,
            "perform_monitoring":True
        }

        #print(data)

        response = requests.post('https://www.site24x7.com/api/maintenance', headers=headers, data=str(data))
        #print(response.text)
        # if "error" in response.keys():
        #     for host in maintenance_list:
        #         print("An error occured posting maintenance for host", host[0], ". Please check info for this host and try again or post manually")
        #print("posting maint for ", id_list, "at", start_date, start_time)
