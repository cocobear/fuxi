#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : access_auth.py
# @Desc    : ""

from flask import request, session
from fuxi.core.databases.orm.auth.user_orm import DBFuxiAdmin
from flask_restful import Resource, reqparse
from fuxi.core.data.response import Response
from fuxi.common.utils.logger import logger
from fuxi.core.auth.token import auth

parser = reqparse.RequestParser()
parser.add_argument('username', type=str)
parser.add_argument('password', type=str)
parser.add_argument('uid', type=int)
parser.add_argument('nick', type=str)
parser.add_argument('email', type=str)


class UserManageV1(Resource):
    @auth
    def post(self):
        try:
            if session.get("authority") != 0:
                return Response.failed(message="添加用户失败: 没有权限")
            args = parser.parse_args()
            username = args['username']
            password = args['password']
            nick = args['nick']
            email = args['email']
            if DBFuxiAdmin.add_admin(
                username=username, password=password,
                nick=nick, email=email, role=1
            ):
                return Response.success(message="添加成功")
            else:
                return Response.failed(message="添加管理员失败", code=10401)
        except Exception as e:
            logger.warning("add admin failed: {}".format(e))
            return Response.failed(message=e)

    @auth
    def put(self):
        try:
            op = session.get("user")
            args = parser.parse_args()
            username = args['username'] if args.get("username") else op
            if not username:
                return Response.failed(message="没有权限")
            password = args['password']
            if op == username or (session.get("authority") == 0):
                if len(password) < 8:
                    return Response.failed(message="密码太短")
                DBFuxiAdmin.change_password(username, password)
                return Response.success(message="你的密码已更改")
            else:
                return Response.failed(message="没有权限")
        except Exception as e:
            logger.warning("password change failed: {}".format(e))
            return Response.failed(message=e)


class TokenManageV1(Resource):
    @staticmethod
    def get():
        try:
            args = parser.parse_args()
            remote_ip = request.remote_addr
            username = args['username']
            password = args['password']
            token = DBFuxiAdmin.get_token(username, password)
            if token:
                logger.success("{} {} authentication success".format(remote_ip, username))
                return Response.success(data=token, message="验证成功")
            else:
                error = "{} authentication failed: {} {}".format(remote_ip, username, password)
                logger.warning(error)
                return Response.failed(message="验证失败", code=10401)
        except Exception as e:
            logger.warning("get token failed: {}".format(e))
            return Response.failed(message=e)

    @staticmethod
    def put():
        try:
            args = parser.parse_args()
            remote_ip = request.remote_addr
            username = args['username']
            password = args['password']
            token = DBFuxiAdmin.refresh_token(username, password)
            if token:
                logger.success("{} {} token refresh success".format(remote_ip, username))
                return Response.success(data=token)
            else:
                error = "{} token refresh failed: {} {}".format(remote_ip, username, password)
                logger.warning(error)
                return Response.failed(message=error, code=10401)
        except Exception as e:
            logger.warning("refresh token failed: {}".format(e))
            return Response.failed(message=e)

