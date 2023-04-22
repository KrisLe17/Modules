import os.path
import inspect
import mysql.connector
from DBModule.DatabaseConfiguration import configuration

class mysql_database:
    def __init__(self, config_file):
        basedir = os.path.dirname(inspect.getfile(configuration))
        config = configuration(os.path.join(basedir, config_file))
        self.mydb = mysql.connector.connect(
        host = "localhost",
        user = config.get_db_write_user(),
        password = config.get_db_write_pass(),
        database = config.get_db_name()
        )
        self.mycursor = self.mydb.cursor(buffered=True, dictionary=True)

    def new_record(self, tablename, params = {}):
        sql = "INSERT INTO {tablename} ({keys}) VALUES ({vals})".format(tablename = tablename, keys=", ".join(params.keys()), vals=", ".join("%s" for val in params.values()))
        val = tuple(params.values())
        self.mycursor.execute(sql, val)
        self.mydb.commit()

    def update_record(self, tablename, record_num, params = {}):
        idname = tablename + "_id"
        for key in params.keys():
            sql = ('UPDATE {tablename} SET ' + key + ' = %s WHERE {idname} = %s').format(tablename = tablename, idname = idname, record_num = record_num)
            self.mycursor.execute(sql, [params[key], record_num])
            self.mydb.commit()

    def match_record(self, tablename, params):
        arr = []
        sql = ('SELECT * FROM {tablename} WHERE ').format(tablename = tablename)
        for key in params:
            arr.append(("{key} = ").format(key = key) + "%s")
        sql +=  ' AND '.join(arr)
        values = list(params.values())
        self.mycursor.execute(sql, values)
        myresult = self.mycursor.fetchall()
        return myresult


    def get_records_by_value(self, tablename, key, value):
        sql = ('SELECT * FROM {tablename} WHERE {key} = %s').format(tablename = tablename, key = key)
        self.mycursor.execute(sql, [value])
        myresult = self.mycursor.fetchall()
        return myresult

    def get_record_like(self, tablename, key, value):
        sql = ('SELECT * FROM {tablename} WHERE {key} LIKE %s').format(tablename = tablename, key=key)
        self.mycursor.execute(sql, [value + '%'])
        myresult = self.mycursor.fetchall()
        #print("like result", myresult)
        return myresult


    def get_record_ids(self, tablename, key, value):
        idname = tablename + "_id"
        sql = ('SELECT {idname} FROM {tablename} WHERE {key} = %s').format(idname = idname, tablename = tablename, key = key)
        self.mycursor.execute(sql, [value])
        myresult = self.mycursor.fetchall()
        results = list(result[idname] for result in myresult)
        return results

    def get_record_by_id(self, tablename, idnum):
        idname = tablename + "_id"
        sql = ('SELECT * FROM {tablename} WHERE {idname} = %s').format(tablename = tablename, idname = idname, idnum = idnum)
        self.mycursor.execute(sql, [idnum])
        myresult = self.mycursor.fetchone()
        return myresult

    def sanitize_value(self, value):
        if isinstance(value, str):
            value = value.strip('"\'\n ')
        return value
    
    def get_all_records(self, tablename):
        sql = ('SELECT * FROM {tablename}').format(tablename = tablename)
        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()
        return myresult
    
    def get_record_count(self, tablename):
        sql = ('SELECT COUNT(*) FROM {tablename}').format(tablename = tablename)
        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()
        return myresult
    
    # def new_user_record(self, tablename, user_name, pwd):
    #     #This is new record except for users, it uses the passhashing set up in obfuscate.py
    #     params = {
    #         "user_name":user_name,
    #         "user_pwd": hash_pass.obf_pass(pwd)
    #     }
    #     sql = "INSERT INTO {tablename} ({keys}) VALUES ({vals});".format(tablename = tablename, keys=", ".join(params.keys()), vals=", ".join("%s" for val in params.values()))
    #     val = tuple(params.values())
    #     self.mycursor.execute(sql, val)
    #     self.mydb.commit()