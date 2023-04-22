#Need to install requests package for python
#easy_install requests
import requests
import os
import inspect
from ServiceNow.configuration import Configuration

class ServiceNow:
    def __init__(self):
        basedir = os.path.dirname(inspect.getfile(Configuration))
        config = Configuration(os.path.join(basedir, 'config.yaml'))
        credentials = config.get_credentials()
        self.url = credentials["url"]
        self.username = credentials["username"]
        self.password = credentials["pass"]
        self.nagios_integration_id = "130f37e3db4c14107f573c00ad961995" #This is the ID assigned to Nagios Integration account
        self.business_service_infrastructure = "ad9318c41342fa00a1547d004244b040" #This is the ID assigned to Infrastructure code
        self.crc_id = "c95ce70913d6c30cbf8e7d004244b0ac" #This is the ID assigned to the CRC group

    def create_incident(self, short_description, description, impact=2, opened_by="130f37e3db4c14107f573c00ad961995", business_service="ad9318c41342fa00a1547d004244b040", caller_id="130f37e3db4c14107f573c00ad961995", assignment_group="c95ce70913d6c30cbf8e7d004244b0ac",
                        urgency=2, category="inquiry", u_outage="No"):

        url = self.url + "now/table/incident"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = str({'short_description':short_description,
                    "description":description,
                    "contact_type":"email",
                    "opened_by":opened_by,
                    "impact":impact,
                    "urgency":urgency,
                    "business_service":business_service,
                    "caller_id":caller_id,
                    "assignment_group":assignment_group,
                    "category": category,
                    "u_outage": u_outage})

        response = requests.post(url, auth=(self.username, self.password), headers=headers, data=data)
        # print('posting alert data: ', data)
        if response.status_code != 201:
            print("Status:", response.status_code, "Headers:", response.headers, "Error Response:", response.json())
            exit()

        data = response.json()
        print(data['result']['number'], ' for ', short_description,' created successfully!')

    def create_request(self, description, opened_by=None):
        url = self.url + "now/table/sc_req_item"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = str({"description":description,
                    "opened_by":opened_by})
        response = requests.post(url, auth=(self.username, self.password), headers=headers, data=data)
        return response

    def get_requests(self):
        #%5E is ^ (logical and), %3D is =
        url = self.url + "now/table/sc_request"
        print(url)
        #response = requests.get(api_url, auth=(self.username, self.password), verify=False, params=params).json()
        #print("get open params:", api_url)
        #print("open tickets:", len(response["result"]), json.dumps(response, indent=2))
        return requests.get(url, auth=(self.username, self.password), verify=False)

    def api_get_open_ticket(self, short_description=None, created_by=None, assignment_group=None):
        #%5E is ^ (logical and), %3D is =
        url = self.url + "incident"
        api_url = url + '?sysparm_query=active%3Dtrue%5Estate%3D1%5EORstate%3D2%5EORstate%3D3' # This makes it return only incidents new/in progress/onhold
        params = {} #hold the parameters we want to search with

        #build up parameters for the search
        if short_description != None:
            api_url += "%5Eshort_description%3D" + short_description
            # params['short_description'] = short_description
        if created_by != None:
            api_url += "%5Ecaller_id%3D" + created_by
            #params['created_by'] = created_by
        if assignment_group != None:
            api_url += "%5Eassignment_group%3D" + assignment_group
            #params['assignment_group'] = assignment_group

        #response = requests.get(api_url, auth=(self.username, self.password), verify=False, params=params).json()
        #print("get open params:", api_url)
        #print("open tickets:", len(response["result"]), json.dumps(response, indent=2))
        return requests.get(api_url, auth=(self.username, self.password), verify=False, params=params).json()

    def get_group_id(self):
        print("group id is ")

    def resolve_incidents(self, response):
        #print("Resolving", response['result'])
        url = self.url + "incident"
        if len(response) != 0:
            data = {'business_service': self.business_service_infrastructure, 
                'contact_type': 'email',
                'assigned_to': self.nagios_integration_id,
                'u_outage': 'No',
                'close_code': 'Solved Remotely (Work Around)',
                'close_notes': 'The alert has cleared. This ticket was automatically closed by Agios automation. Please reach out to the CRC if you have any questions or concerns.',
                'incident_state': '6'
                }

            for x in range(len(response)):
                print("closed ticket:", response[x]['short_description'])
                requests.put(url + '/' + response[x]['sys_id'], auth=(self.username, self.password), verify=False,
                             data=str(data))    

        else:
            print("No tickets were found that were eligible for closing.")
