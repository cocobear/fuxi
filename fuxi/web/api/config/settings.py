#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/1/17
# @File    : settings.py
# @Desc    : ""

from flask import session
from flask_restful import Resource, reqparse
from fuxi.core.auth.token import auth
from fuxi.core.data.response import Response
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.core.databases.orm.auth.user_orm import DBFuxiAdmin
from fuxi.core.databases.orm.configuration.config import DBFuxiConfiguration
from fuxi.common.utils.logger import logger

parser = reqparse.RequestParser()
parser.add_argument('username', type=str)
parser.add_argument('password', type=str)
parser.add_argument('nick', type=str)
parser.add_argument('email', type=str)
parser.add_argument('key', type=str)
parser.add_argument('value', type=str)


class ConfigManageV1(Resource):
    @auth
    def get(self):
        """
        GET /api/v1/settings
        :return:
        """
        try:
            # pass
            return Response.success()
        except Exception as e:
            msg = "设置失败: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class AccountManageV1(Resource):
    @auth
    def get(self):
        """
        GET /api/v1/settings/user
        """
        data = []
        try:
            items = DBFuxiAdmin.get_user_list()
            for item in items:
                item['uid'] = str(item['_id'])
                item['date'] = timestamp_to_str(item['date'])
                if item['role'] == 0:
                    item['role'] = "admin"
                else:
                    item['role'] = "user"
                del item['_id']
                data.append(item)
            return Response.success(data=data)
        except Exception as e:
            msg = "设置失败: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def delete(self, uid):
        """
        DELETE /api/v1/settings/user/<uid>
        """
        try:
            if session.get("authority") == 0 and not DBFuxiAdmin.is_admin(uid):
                DBFuxiAdmin.delete_by_id(uid)
                return Response.success(message="删除成功")
            else:
                return Response.failed(message="删除用户失败: 没有权限")
        except Exception as e:
            msg = "删除用户失败: {} {}".format(uid, e)
            logger.warning(msg)
            return Response.failed(message=msg)

    @auth
    def put(self, uid):
        """
        PUT /api/v1/settings/user/<uid>
        """
        try:
            if session.get("authority") != 0:
                return Response.failed(message="修改用户信息失败: 没有权限")
            args = parser.parse_args()
            username = args['username']
            nick = args['nick']
            email = args['email']
            DBFuxiAdmin.update_by_id(uid, {
               "username": username,
               "nick": nick,
               "email": email,
            })
            return Response.success(message="修改用户信息成功")
        except Exception as e:
            logger.warning("修改用户信息失败: {}".format(e))
            return Response.failed(message=e)


class BasicConfigMangeV1(Resource):
    @auth
    def get(self):
        """
        GET /api/v1/settings/basic
        """
        data = []
        try:
            # pass
            item = DBFuxiConfiguration.find_one()
            if item:
                data.append({"key": "whatweb_exe", "desc": "Whatweb"})
                data.append({"key": "nmap_exe", "desc": "Nmap"})
                data.append({"key": "sqlmap_api", "desc": "SQLMAP API"})
                for i in data:
                    i['cid'] = str(item['_id'])
                    i['value'] = item[i['key']]
            return Response.success(data=data)
        except Exception as e:
            msg = "设置失败: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def put(self, cid):
        try:
            args = parser.parse_args()
            key = args['key']
            value = args['value']
            if not key or not value:
                return Response.failed(message="非法输入!")
            if not DBFuxiConfiguration.setting_item_check(key.strip()):
                return Response.failed(message="配置项目无效")
            d = {key.strip(): value.strip()}
            DBFuxiConfiguration.update_by_id(cid, d)
            return Response.success(message="更新成功")
        except Exception as e:
            msg = "更新失败: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)

