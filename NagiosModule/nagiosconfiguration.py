import yaml

class Configuration:
    def __init__(self, file_path):
        config_file = open(file_path, "r")
        self.config_data = yaml.load(config_file, Loader=yaml.FullLoader)

    def get_board_configs(self):
        return self.config_data["boards"]

    def get_credentials(self):
        return self.config_data["credentials"]


