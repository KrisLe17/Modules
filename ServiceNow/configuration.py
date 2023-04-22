import yaml

class Configuration:
    def __init__(self, file_path):
        config_file = open(file_path, "r")
        self.config_data = yaml.load(config_file, Loader=yaml.FullLoader)

    def get_board_configs(self):
        return self.config_data["boards"]

    def get_credentials(self):
        return self.config_data["credentials"]

    def get_iteration_time(self):
        return self.config_data["iteration_time"]

if __name__ == "__main__":
    config = Configuration(r"config.yaml")
    print(type(config.get_iteration_time()))
