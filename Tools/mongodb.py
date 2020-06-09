# -*-coding: utf-8 -*-

import traceback
from pymongo import MongoClient
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern
from Env import env_config as cfg
from gridfs import GridFS
from bson.objectid import ObjectId
from Common.com_func import log
from Common.test_func import mongo_exception_send_DD
from dateutil import parser

import base64


db_pool = {}


class MongodbUtils(object):
    """
    此类用于链接mongodb数据库
    write_concern='majority'：表示所有节点写入成功后，才算成功
    write_concern=2： 表示只需要两个节点写入成功后，即为成功
    """
    def __init__(self, collection="", ip="", port=None, database="",
                 replica_set_name="", read_preference=ReadPreference.SECONDARY_PREFERRED,
                 write_concern="majority"):

        self.collection = collection
        self.ip = ip
        self.port = port
        self.database = database
        self.replica_set_name = replica_set_name
        self.read_preference = read_preference
        self.write_concern = write_concern

        if (ip, port) not in db_pool:
            db_pool[(ip, port)] = self.db_connection()
        elif not db_pool[(ip, port)]:
            db_pool[(ip, port)] = self.db_connection()

        self.db = db_pool[(ip, port)]
        self.db_table = self.db_table_connect()

    def __enter__(self):
        return self.db_table

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def db_connection(self):
        db = None
        try:
            if self.replica_set_name:
                # 当pymongo更新到3.x版本, 连接副本集的方法得用MongoClient, 如果版本<=2.8.1的, 得用MongoReplicaSetClient
                db = MongoClient(self.ip, replicaset=self.replica_set_name)
            else:
                db = MongoClient(self.ip, self.port)
            log.info("mongodb connection success")

        except Exception as e:
            log.error("mongodb connection failed: %s" % self.collection)
            print(e)
            print(traceback.format_exc())
        return db

    def db_table_connect(self):
        db = self.db.get_database(self.database, read_preference=self.read_preference,
                                  write_concern=WriteConcern(w=self.write_concern))
        table_db = db[self.collection]
        return table_db


class MongoGridFS(object):
    """
     备注：
       （1）保存在mongo的'image'数据库中，没有会自动创建
       （2）创建成功后，会在集合中生成'fs.flies'和'fs.chunks'
    """

    def __init__(self):
        self.client = MongoClient("mongodb://" + cfg.MONGODB_ADDR)
        self.img_db = self.client["image"]
        self.fs = GridFS(database=self.img_db, collection="fs")

    def upload_file(self, img_file_full):
        """
        上传图片
        :param img_file_full:
        :return:
            1.上传成功 -> 返回 图片id
            2.mongo连接不上 -> 返回 None
        """
        img_file = img_file_full.split("/")[-1]
        img_name = img_file.split(".")[0]
        img_tpye = img_file.split(".")[1]
        files_id = None
        try:
            with open(img_file_full, 'rb') as file_r:
                object_id = self.fs.put(data=file_r, content_type=img_tpye, filename=img_name)
                files_id = str(object_id)
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="上传图片")
        finally:
            return files_id

    def get_base64_by_id(self, file_id):
        """
        按文件'file_id'获取图片'base64码'
        :param file_id:
        :return:
            1.获取成功 -> 返回 图片二进制文件
            2.找不到该文件 -> 返回 no such file
            3.mongo连接不上 -> 返回 None
        """
        img_base64 = None
        try:
            gf = self.fs.get(file_id=ObjectId(file_id))
            img_binary = gf.read()
            img_base64 = str(base64.b64encode(img_binary))[2:-1]
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="获取二进制图片")
            if "Connection refused" not in str(e):
                img_base64 = "no such file"
        finally:
            # log.info("img_base64 : " + str(img_base64))
            return img_base64

    def download_file_by_name(self, file_name, out_name):
        """
        按文件名获取图片，保存到'out_name'中
        :param file_name:
        :param out_name:
        :return:
        """
        try:
            img_binary = self.fs.get_version(filename=file_name, version=1).read()
            with open(out_name, 'wb') as file_w:
                file_w.write(img_binary)
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="获取图片")

    def del_file_by_date(self, date_str):
        """
        删除指定日期之前的所有图片
        :param date_str: 必须是'ISODate'类型的字符串 -> 2020-03-02T15:51:05
        :return:
           {"uploadDate" : {"$lt": ISODate("2020-03-02T15:51:05")}}
        """
        try:
            ISODate = parser.parse(date_str)
            query_dict = {"uploadDate": {"$lt": ISODate}}
            grid_outs = self.fs.find(query_dict)
            file_id_list = []
            for grid_out in grid_outs:
                log.info(grid_out.__dict__)
                file_id_list.append(str(grid_out._file.get("_id")))
            for file_id in file_id_list:
                self.fs.delete(file_id=ObjectId(file_id))
            return len(file_id_list)
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="删除图片")
            return None


if __name__ == '__main__':

    # with MongodbUtils(ip=cfg.MONGODB_IP_PORT, database="monitorAPI", collection="monitorResult") as monitor_db:
    #     res = monitor_db.find_one({"testCaseName": "获取图片验证码_200_MONITOR"}, {"_id": 0})
    #     print(res)
    #     print(monitor_db)

    img_file_full = cfg.SCREENSHOTS_DIR + "TrainTest/test_ctrip/search_train_1.png"
    mgf = MongoGridFS()
    # mgf.upload_file(img_file_full)
    mgf.get_base64_by_id("5e61152ff0dd77751382563f")
    # mgf.download_file_by_name("search_train_3", "/Users/micllo/Downloads/test2.png")
