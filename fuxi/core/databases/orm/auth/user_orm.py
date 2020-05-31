#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/5
# @File    : user.py
# @Desc    : ""

import os
import time
import hashlib
from bson import ObjectId
from secrets import token_hex
from fuxi.common.utils.logger import logger
from fuxi.core.databases.db_mongo import mongo, T_ADMIN
from fuxi.core.databases.db_error import DatabaseError
from fuxi.core.databases.orm.database_base import DatabaseBase


class _DBFuxiAdmin(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_ADMIN
        self.urandom_count = 16

    def find_one(self):
        return mongo[self.table].find_one()

    def get_user_list(self):
        return mongo[self.table].find({}, {"salt": 0, "password": 0, "token": 0})

    def is_admin(self, uid):
        item = mongo[self.table].find_one({"_id": ObjectId(uid)})
        if item and item['role'] == 0:
            return True
        else:
            return False

    def add_admin(self, username, password, role=0, nick=None, email=None):
        if not self._user_check(username):
            raise DatabaseError("用户名已经存在")
        if username and password:
            try:
                salt = token_hex()[8:16]
                item = mongo[self.table].insert_one({
                    "username": username,
                    "salt": salt,
                    "password": self.hash_md5(password, salt),
                    "role": role,
                    "token": self.generate_token(),
                    "nick": nick if nick else username,
                    "email": email if email else "admin@fuxi.com",
                    "date": int(time.time())
                })
                return item
            except Exception as e:
                logger.warning("admin insert failed: {} {}".format(username, e))
                return False
        else:
            logger.warning("admin insert failed: invalid data")
            return False

    def _user_check(self, username):
        if mongo[self.table].find_one({"username": username}):
            return False
        return True

    def refresh_token(self, username, password):
        if self.passwd_check(username, password):
            token = self.generate_token()
            mongo[self.table].update_one({"username": username}, {"$set": {"token": token}})
            return token
        else:
            return ""

    def get_token(self, username, password):
        if self.passwd_check(username, password):
            return mongo[self.table].find_one({"username": username}, {"token": 1})['token']
        else:
            return ""

    def passwd_check(self, username, password):
        item = mongo[self.table].find_one({"username": username})
        if item:
            if item['password'] == self.hash_md5(password, item['salt']):
                return True
        raise DatabaseError("用户名或密码错误")

    def token_check(self, token):
        item = mongo[self.table].find_one(
            {"token": str(token)},
            {"_id": 0, "username": 1, "nick": 1, "email": 1, "role": 1, "date": 1}
        )
        return item if item else False

    def generate_token(self):
        return hashlib.sha1(os.urandom(self.urandom_count)).hexdigest()

    def get_user_info_by_token(self, token):
        if self.token_check(token):
            return mongo[self.table].find_one(
                {"token": token}, {"username": 1, "nick": 1, "email": 1}
            )
        else:
            raise DatabaseError("TOKEN无效")

    def change_password(self, username, password):
        salt = token_hex()[8:16]
        mongo[self.table].update_one(
            {"username": username},
            {"$set": {"salt": salt, "password": self.hash_md5(password, salt), "token": self.generate_token()}}
        )
        return ""

    @staticmethod
    def hash_md5(password, salt):
        md5_obj = hashlib.md5()
        md5_obj.update("{}{}".format(password, salt).encode('utf-8'))
        return md5_obj.hexdigest()


DBFuxiAdmin = _DBFuxiAdmin()

