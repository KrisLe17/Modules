import yaml

class configuration:
    def __init__(self, file_path):
        self.file_name = file_path
        config_file = open(file_path, "r")
        self.config_data = yaml.load(config_file, Loader=yaml.FullLoader)

    def get_db_name(self):
        return self.config_data["db_name"]

    def get_db_read_user(self):
        return self.config_data["db_read_user"]

    def get_db_read_pass(self):
        return self.config_data["db_read_pass"]

    def get_db_write_user(self):
        return self.config_data["db_write_user"]

    def get_db_write_pass(self):
        return self.config_data["db_write_pass"]