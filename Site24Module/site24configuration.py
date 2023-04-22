import yaml

class Configuration:
    def __init__(self, file_path):
        self.file_name = file_path
        config_file = open(file_path, "r")
        self.config_data = yaml.load(config_file, Loader=yaml.FullLoader)

    def get_client_details(self):
        return self.config_data["client"]
    
    def get_all_ops_read_refresh_token(self):
        return self.config_data["all_ops_refresh"]

    # def update_account_read_refresh_token(self, token):
    #     self.config_data["account_read_refresh_token"] = token
    #     with open(self.file_name, "w") as config:
    #         config.write(yaml.dump(self.config_data, default_flow_style=False))

    def get_bu_configs(self):
        return self.config_data["business_units"]



# ****************************************************************
# Below Code is currently unused. This is for getting business unit ids
# and msp ids if needed in future. These are hard coded at the moment.
# New business units will require an update to code
# ****************************************************************

# get msp Zaaid for our account
# site24x7.msp.read
#
# msp_tokens = Authorization.get_acc_token(msp_read_refresh_token, 'Site24x7.MSP.Read')
# msp_acc_token = msp_tokens[0]
# msp_refresh_token = msp_tokens[1]
# print("msp acc: ", msp_acc_token)
# print("msp refresh: ", msp_refresh_token)
# if msp_refresh_token != None:
#     print("updating msp read token in config")
#     config.update_msp_read_refresh_token(msp_refresh_token, config)
#
# headers = {
#     "Content-Type": "application/json;charset=UTF-8",
#     "Accept": "application/json; version = 2.0",
#     "Authorization" : "Zoho-oauthtoken " + msp_acc_token
# }
#
# account_id = requests.get("https://www.site24x7.com/api/short/msp/customers", headers = headers).json()
#print("Msp account: ", account_id)

#get business unit ids for our account
#site24x7.bu.read

# bu_tokens = Authorization.get_acc_token(bu_read_refresh_token, 'Site24x7.Bu.Read')
# bu_acc_token = bu_tokens[0]
# bu_refresh_token = bu_tokens[1]
# #print("bu acc: ", bu_acc_token)
# #print("bu refresh: ", bu_refresh_token)
# if bu_refresh_token != None:
#     print("updating bu read token in config")
#     config.update_bu_read_refresh_token(bu_refresh_token, config)
#
# headers = {
#     "Content-Type": "application/json;charset=UTF-8",
#     "Accept": "application/json; version = 2.0",
#     "Authorization" : "Zoho-oauthtoken " + bu_acc_token
# }
#
# account_id = requests.get("https://www.site24x7.com/api/short/bu/business_units", headers = headers).json()
#print("Business account: ", account_id)

