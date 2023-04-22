import json
import requests
from datetime import datetime
from datetime import timedelta
import pytz

class Agios:
    def __init__(self, api_key, api_host, timezone, should_verify_https_cert=True):
        self.api_key = api_key
        self.api_host = api_host
        self.should_verify_https_cert = should_verify_https_cert
        self.connected = True # This will be used to skip tickets from the board for closing if the script couldn't connect to the board
        self.hosts_on_scheduled_downtime = self.get_hosts_on_scheduled_downtime()
        self.timezone = timezone
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.params = {'apikey': str(self.api_key),
                        'pretty': '1'}
        self.api_url = "https://{api_host}/nagiosxi/api/v1/".format(api_host=self.api_host)

    def api_get(self, component, filters=[]):
        try:
            api_url = "https://{api_host}/nagiosxi/api/v1/objects/{component}?apikey={key}&{filters}".format(
                api_host=self.api_host, component=component, key=self.api_key, filters="&".join(filters))
            result = requests.get(api_url, timeout=15, verify=self.should_verify_https_cert).text
            if result[0] != "{":
                result = json.loads(result[result.find("{"):])
            else:
                result = json.loads(requests.get(api_url, verify=self.should_verify_https_cert).text)
        except Exception as e:
            print("An error occurred when connecting to NagiosXI: ", self.api_host, ". Please check connectivity and API parameters")
            print(e)
            result = {}
        return result

    def get_config(self, component):
        try:
            api_url = "https://{api_host}/nagiosxi/api/v1/config/{component}?apikey={key}".format(
                api_host=self.api_host, component=component, key=self.api_key)
            result = json.loads(requests.get(api_url, verify=self.should_verify_https_cert).text)
        except Exception as e:
            print("An error occurred when connecting to NagiosXI: ", self.api_host, ". Please check connectivity and API parameters")
            print(e)
            self.connected = False
        return result

     ############## UNUSED ######################
    # def api_new_monitor(self, component, host_name=None, ip=None, config_name=None, service_description=None, check_command=None):
    #     try:
    #         #data = 'host_name=testapihost&address=127.0.0.1&check_command=check_ping\\!3000,80%\\!5000,100%&max_check_attempts=2&check_period=24x7&contacts=nagiosadmin&notification_interval=5&notification_period=24x7&applyconfig=1'
    #         api_url = "https://{api_host}/nagiosxi/api/v1/config/{component}".format(
    #             api_host=self.api_host, component=component)
    #         service_description = service_description.replace(" ", "_")
    #         service_description = service_description.replace("/", "LIN")
    #         if component == "service":
    #             data = {"service_description":service_description,
    #             "config_name":config_name,
    #             "host_name":service_description,
    #             "check_command":check_command,
    #             "max_check_attempts":2,
    #             "check_period":"24x7",
    #             "check_interval":5,
    #             "retry_interval":5,
    #             "contacts":"nagiosadmin",
    #             "notification_interval":5,
    #             "notification_period":"24x7",
    #             "applyconfig":1}
    #         else:
    #             print("adding host", host_name)
    #             data = {"host_name":host_name,
    #             "address":ip,
    #             "use": "xiwizard_windowsserver_host",
    #             "max_check_attempts":2,
    #             "check_period":"24x7",
    #             "contacts":"nagiosadmin",
    #             "notification_interval":5,
    #             "notification_period":"24x7",
    #             "applyconfig":1}
    #         data_str = ""
    #         for key in data:
    #             data_str += key + "=" + str(data[key]) + "&"
    #         # print(api_url)
    #         # print("datastr", data_str[:-1])
    #         result = requests.post(api_url, headers=self.headers, params=self.params, timeout=15, verify=self.should_verify_https_cert, data=data_str[:-1]).text
    #     except Exception as e:
    #         print("An error occurred when attempting to post to NagiosXI: ", self.api_host, ". Please check connectivity and API parameters")
    #         print(e)
    #         result = {}
    #     return result

    # def api_new_group(self, component, group_name, alias, members=[]):
    #     try:
    #         api_url = "https://{api_host}/nagiosxi/api/v1/config/{component}?apikey={key}".format(
    #             api_host=self.api_host, component=component, key=self.api_key)
    #     except:
    #         print("broke it")
    #     return

    # def api_update_group(self, component, group_name, members=[]):
    #     try:
    #         api_url = "https://{api_host}/nagiosxi/api/v1/config/{component}/{group_name}".format(
    #             api_host=self.api_host, component=component, group_name=group_name)
    #         data = "members=" + ",".join(members) + "&applyconfig=1"
    #         print("members are", data)
    #         result = requests.put(api_url, headers=self.headers, params=self.params, timeout=15, verify=self.should_verify_https_cert, data=data).text
    #         print("Group update result is", result)
    #     except Exception as e:
    #         print("Error occurred trying to update", group_name)
    #         print(e)
    #     return result

    # def api_update_service(self, service_description, config_name, members=[]):
    #     try: ##maybe I can use %2F instead of /? otherwise have to get rid of the /
    #         service_description = service_description.replace(" ", "_")
    #         service_description = service_description.replace("/", "LIN")
    #         config_name = config_name.replace(" ", "_")
    #         config_name = config_name.replace("/", "LIN")
    #         api_url = "https://{api_host}/nagiosxi/api/v1/config/service/{config_name}/{service_description}?apikey={api_key}&".format(
    #             api_host=self.api_host, config_name=config_name, service_description=service_description.replace("/", "%2F") if "/" in service_description else service_description, api_key=self.api_key)
    #         data = {"host_name": members,
    #             "applyconfig":1}
    #         data_str = ""
    #         for key in data:
    #             if key == "host_name":
    #                 data_str += key + "=" + ",".join(data[key]) + "&"
    #             else:
    #                 data_str += key + "=" + str(data[key]) + "&"
    #         api_url += data_str[:-1]
    #         print(api_url)
    #         result = requests.put(api_url, timeout=15, verify=self.should_verify_https_cert).text
    #         #print("Service update result is", result)
    #     except Exception as e:
    #         print("Error occurred trying to update", service_description)
    #         print(e)
    #     return result

    def normalize_nagios_api_response_for_object(self, api_response, object):
        if type(api_response[object]) == type(list()):
            return api_response
        api_response[object] = [api_response[object]]
        return api_response

    def get_objects_with_states(self, object, states, ack):
        states = states if type(states) == type(list()) else [states]
        objects = []

        for state in states:
            if ack:
                statuses = self.api_get(object, filters=["current_state={}".format(state),
                                     "notifications_enabled=1", "scheduled_downtime_depth=0"])
            else: 
                statuses = self.api_get(object, filters=["current_state={}".format(state),
                                        "problem_acknowledged=0", "notifications_enabled=1", "scheduled_downtime_depth=0"])
            if object not in statuses: ## prevents a key error if the object is not in the status aka empty dict
                return []
            self.normalize_nagios_api_response_for_object(statuses, object)
            # for i, status in enumerate(statuses[object]):
            #     if status["scheduled_downtime_depth"] != "0":
            #         statuses[object].pop(i)

            objects += list(statuses[object]) if object in statuses else []

            # print("status test:", statuses)

        # print("Objects:", json.dumps(objects, indent=4))
        return objects

    def get_hosts_on_scheduled_downtime(self):
        """
        This function is necessary because some people schedule downtime on the host, but forget to select the option to
        also schedule downtime on associated services, and, when this happens, the URL parameter we use to filter down
        hosts from API queries doesn't work.
        """
        # Get hosts, filtering for hosts on scheduled downtime
        query_results = self.api_get("hoststatus")
        if "hoststatus" in query_results:
            hoststatus = query_results["hoststatus"]
            if type(hoststatus) == type(list()):
                hosts_in_downtime = []
                for host in query_results["hoststatus"]:
                    if host["scheduled_downtime_depth"] != "0":
                        #print(host)
                        hosts_in_downtime.append(host["host_name"] if "host_name" in host else host["name"])
                return hosts_in_downtime
            else:
                # If there's a single alert, we're not given an array
                return hoststatus["name"]
        else:
            # If there are no hosts on scheduled downtime, return an empty array
            return []

    def filter_hosts_on_scheduled_downtime(self, alerts):
        # hostname_key = "host_name" if contains_service_alerts else "name"

        focused = []
        for alert in alerts:
            hostname_key = "host_name" if "host_name" in alert else "name"
            if not(alert[hostname_key] in self.hosts_on_scheduled_downtime):
                focused.append(alert)

        return focused

    def get_service_alerts(self, ack=False):
        service_alerts = self.get_objects_with_states("servicestatus", [1, 2], ack)
        return self.filter_hosts_on_scheduled_downtime(service_alerts)

    def get_host_alerts(self, ack=False):
        host_alerts = self.get_objects_with_states("hoststatus", 1, ack)
        return self.filter_hosts_on_scheduled_downtime(host_alerts)

    def determine_duration(self, alert):
        local = pytz.timezone(self.timezone)
        nagios_local_time = datetime.strptime(alert["last_state_change"], '%Y-%m-%d %H:%M:%S')
        nagios_utc = local.localize(nagios_local_time, is_dst=True)
        nagios_utc = nagios_utc.astimezone(pytz.utc)
        nagios_utc = nagios_utc.replace(tzinfo=None)

        return((datetime.utcnow() - nagios_utc).total_seconds() / 60.0)

    def filter_newer_alerts(self, alerts, warning_time, critical_time):
        # alerts = self.get_service_alerts() + self.get_host_alerts()
        alerts = filter(lambda input: type(input) == type(dict()), alerts)
        filtered_alerts = []
        for alert in alerts:
            # convert the time the alert started firing to UTC (It's in local...)
            local = pytz.timezone(self.timezone)
            nagios_local_time = datetime.strptime(alert["last_state_change"], '%Y-%m-%d %H:%M:%S')
            nagios_utc = local.localize(nagios_local_time, is_dst=True)
            nagios_utc = nagios_utc.astimezone(pytz.utc)
            nagios_utc = nagios_utc.replace(tzinfo=None)

            duration = (datetime.utcnow() - nagios_utc).total_seconds() / 60.0
            alert_state = int(alert["current_state"])
            if (alert_state == 1 and duration > warning_time) or (alert_state == 2 and duration > critical_time):
                filtered_alerts.append(alert)
        return filtered_alerts

    def get_alerts_to_handle(self, ack, warning_time=30, critical_time=20, host_time=10):
        service_alerts = self.filter_newer_alerts(self.get_service_alerts(ack), warning_time, critical_time)
        host_alerts = self.filter_newer_alerts(self.get_host_alerts(ack), host_time, host_time) # TODO Cleanup

        # print("New:", host_alerts)
        # print("Host alerts:", json.dumps(self.get_objects_with_states("hoststatus", 1), indent=4))
        # print("Host alerts:", host_alerts)
        # print("Service alerts:", service_alerts)
        return service_alerts + host_alerts

    def group_alerts_by_host(self, ack=False):
        alerts = self.get_alerts_to_handle(ack)
        grouped_alerts = {}
        for alert in alerts:
            if "service_description" in alert.keys():
                alert["status_text"] = alert["status_text"] if "status_text" in alert else alert["output"]
                if alert["host_name"] in grouped_alerts: #If the host already has an alert in the table, add the next alert to the list under service
                    if "Return code of 255 for service" in alert["status_text"]: ## TODO: add this as adjustable filter function
                        print("Dropping Ticket for 255 Alert")
                    else:
                        grouped_alerts[alert["host_name"]]["service"].append(alert["display_name"])
                        grouped_alerts[alert["host_name"]]["service_status"].append(alert["status_text"]  + "\n")
                        duration = self.determine_duration(alert)
                        if duration > grouped_alerts[alert["host_name"]]["duration"]:
                            grouped_alerts[alert["host_name"]]["duration"] = duration
                else: #Create a dict with the alert information under the host name
                    #print(alert)
                    if "Return code of 255 for service" in alert["status_text"]:
                        print("Dropping Ticket for 255 Alert") #skip 255 alerts hopefully
                    else:
                        grouped_alerts[alert["host_name"]] = {
                            "board": self.api_host,
                            "ip": alert["host_address"] if "host_address" in alert else alert["address"],
                            "service": [alert["display_name"]],
                            "service_status": [alert["status_text"] if "status_text" in alert else alert["output"] + "\n"],
                            "state": ("CRITICAL", "WARNING") [alert["current_state"] == "1"],
                            "duration": self.determine_duration(alert),
                            "impact": 2}
            else: #no service_description THIS IS A HOST ALERT
                    grouped_alerts[alert["host_name"]] = {
                        "board": self.api_host,
                        "ip": alert["address"],
                        "service": [alert["display_name"]],
                        "service_status": [alert["output"] + "\n"],
                        "state": "DOWN",
                        "duration": self.determine_duration(alert),
                        "impact": 1}

        return grouped_alerts

    def post_maint(self, maintenance_list): #post maintenance to the Nagios board from the host list sent over using start datetime obj and enddatetime calculated from duration
        start_date = maintenance_list[0][1]
        start_time = maintenance_list[0][2]
        date_time = datetime.combine(start_date, start_time)
        duration = timedelta(minutes=int(maintenance_list[0][3]))
        end_datetime = date_time + duration
        host_list = [host[0] for host in maintenance_list]
        #print("host list", host_list, flush=True)

        #Nagios uses timestamps for posts, convert here
        start_date = datetime.timestamp(date_time)
        end_date = datetime.timestamp(end_datetime)
        
        data = {
            "comment":"API Maintenance",
            "start": start_date,
            "end": end_date,
            "hosts": host_list
        }
        #Nagios only accepts data as a string, not a dict...
        #data = 'comment=Test downtime creation&start=1670986114&end=1670993314&hosts[]=localhost'
        data_str = ""
        #print(data)
        for key, value in data.items():
            if key == "hosts":
                for host in value:
                    data_str += key + "[]=" + str(host) + "&"
            else:
                data_str += key + "=" + str(value) + "&"
        data_str = data_str[:-1] #chop off last &

        api_url = "https://{api_host}/nagiosxi/api/v1/system/scheduleddowntime?".format(
                api_host=self.api_host)
        response = requests.post(api_url, params=self.params, headers=self.headers, data=data_str, verify=False)

        #print(response.text, flush=True)
