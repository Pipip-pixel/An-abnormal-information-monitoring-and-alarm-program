#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/27 17:43
@File    : login.py
@Software: PyCharm
"""
import configparser
import time
import traceback

from my_logger import Logger
from my_requests import HTTPClient

log = Logger(log_name=__name__)
logger = log.get_logger()

# 配置缓存
config = configparser.ConfigParser()
config.read('config.ini')

# 获取缓存有效期配置（单位为秒）
TOKEN_EXPIRY = int(config.get('cache', 'token_expiry', fallback=72000))

# 全局缓存变量，缓存token和缓存时间
token_cache = {
    'a':
        {
            'token': None,
            'timestamp': 0
        },
    'b':
        {
            'token': None,
            'timestamp': 0
        }
}


def get_cached_token(_type):
    """
    获取缓存中的token，如果缓存未过期则返回缓存的token
    """
    current_time = int(time.time())
    if token_cache[_type]['token'] and (current_time - token_cache[_type]['timestamp'] < TOKEN_EXPIRY):
        logger.info("使用缓存的token")
        return token_cache[_type]['token']
    else:
        # 如果缓存过期或没有缓存，返回None
        return None


def set_cached_token(_type, token):
    """
    设置缓存中的token和时间戳
    """
    token_cache[_type]['token'] = token
    token_cache[_type]['timestamp'] = int(time.time())


def loginA():
    """
    登录A系统，增加缓存机制
    """
    # 尝试从缓存中获取token
    cached_token = get_cached_token(_type='a')
    if cached_token:
        return cached_token

    url = "http://10.99.****"
    headers = {
        "Host": "10.99.95.169",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Resource-Id": "undefined",
        "captcha": "487f1ed6-eb29-46d8-8dc1-3514f4ed37e4",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "a_token": "Ym1sdFpHRmplWHBsY205TmIySnBiR1V3Wm1Kak56TTJPVFF6TUdSaFpEazRNR1poTkdVMU1EWTBaamRsTjJVNVpRPT0=",
        "token": "undefined",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "http://10.99.***",
        "Referer": "http://10.99.****",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }
    data = {
        "device_id": "****************",
        "platform": "应用平台",
        "platform_type": "PC",
        "type": "more",
        "company_id": None,
        "verCode": ""
    }

    try:
        client = HTTPClient(retries=3, backoff_factor=1, timeout=5)
        response = client.post(caller_name='loginA', url=url, headers=headers, json=data)
        token = response.headers['Token']
        # 存储获取到的token和时间戳
        set_cached_token(_type='a', token=token)
        return token
    except Exception:
        logger.error(f"请求登录二维码系统出错: {traceback.format_exc()}")
        raise


def loginB():
    """
    登录行业调控系统，增加缓存机制
    """
    # 尝试从缓存中获取token
    cached_token = get_cached_token(_type='b')
    if cached_token:
        return cached_token

    url = "http://10.99.95.*****"
    headers = {
        "Host": "10.99.95..*****",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://10.99.95..*****",
        "Refer": "http://10.99.95..*****/"
    }
    data = {
        "username": ".*****",
        "password": ".**********"
    }

    try:
        client = HTTPClient(retries=3, backoff_factor=1, timeout=5)
        response = client.post(caller_name='loginB', url=url, headers=headers, data=data)
        response = response.json()
        token = response.get("result").get("accessCredentials")

        # 存储获取到的token和时间戳
        set_cached_token(_type='b', token=token)
        return token
    except Exception:
        logger.error(f"请求登录行业调控系统出错: {traceback.format_exc()}")
        raise


if __name__ == '__main__':
    loginA()
    loginB()