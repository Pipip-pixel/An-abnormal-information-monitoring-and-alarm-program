#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/28 9:26
@File    : common.py
@Software: PyCharm
"""
import configparser
import os
import smtplib
import sys
import threading
import traceback
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from constans import html_message, FAIL_TYPE_DICT, STATIC_DATE_END, html_message_body, STYLE, STATIC_DATE_START
from my_logger import Logger
from my_requests import HTTPClient

log = Logger(__name__)
logger = log.get_logger()
# 全局集合和锁
processed_serials = set()
lock = threading.Lock()


def query_b(token, fail_code):
    url = "http://token地址获取"
    headers = {
        "Host": "token地址获取",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "securitytoken": token,
        "Referer": "token地址获取",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }
    params = {
        "qrCode": fail_code,
        "selectMode": 3
    }
    try:
        client = HTTPClient(retries=3, backoff_factor=1, timeout=10)
        response = client.get(caller_name='query_b', url=url, headers=headers, params=params)

        # 解析JSON数据
        json_data = response.json()
        if json_data['code'] == '200' and len(json_data['data']) > 0:
            json_data = json_data['data'][0]
            prod_list = json_data['prodList']
            prod = prod_list[0]
            if len(prod_list) > 0:
                return {
                    'serialnumOld': json_data['serialnumOld'],
                    'produceTime': prod['produceTime'],
                    'machineName': prod['machineName'],
                    'groupName': prod['groupName'],
                    'brand': json_data['brand'],
                    'seqnum': prod['seqnum']
                }
    except Exception:
        # 捕获网络请求异常
        logger.error(f"请求查询B系统失败: {traceback.format_exc()}")
        return False


def get_total_num_for_z(token):
    # 设置请求的URL和参数
    url = "http://10.***" # 设置请求的URL和参数
    if os.environ.get("debug") == "true":
        start_date = STATIC_DATE_START
        end_date = STATIC_DATE_END
    else:
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
    params = {
        'startDate': start_date,
        'endDate': end_date,
        'field': 'create_time',
        'order': 'asc',
        'qrCode': '',
        'page': 1,
        'perPage': 15,
        'status': 1,
        'uploadType': 'UT01'
    }

    # 设置请求头
    headers = {
        'Host': '10.****',
        'Connection': 'keep-alive',
        'Resource-Id': '300040504',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'Accept': 'application/json, text/plain, */*',
        "content-type": "application/json",
        'token': token,
        'Referer': '*****',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
    }

    client = HTTPClient(retries=3, backoff_factor=1, timeout=5)
    try:
        # 发送GET请求
        response = client.get(caller_name='get_total_num_for_z', url=url, headers=headers, params=params)
        response = response.json()
        return response['data']['totalNum']
    except Exception:
        logger.error(f"查询Z失败，{traceback.format_exc()}")
        return False


def get_request_to_shutdown(token):
    # 设置请求的URL
    url = "http://10.99*****"

    # 设置请求头
    headers = {
        'Host': '10.99****',
        'Connection': 'keep-alive',
        'Content-Length': '166',  # 这个字段可以不用设置，requests会自动计算
        'Resource-Id': '300011605',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
        'token': token,
        'Origin': 'http://10.99***',
        'Referer': 'http://10.99.***',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
    }

    # 请求体（请求的JSON数据）
    data = {
        "executorParam": "8",
        "executorHandler": "****",
        "jobDesc": "数据上报",
        "scheduleConf": "*******",
        "triggerStatus": "0",
        "id": 102
    }

    try:
        client = HTTPClient(retries=3, backoff_factor=1, timeout=5)
        client.post(caller_name='get_request_to_shutdown', url=url, headers=headers, json=data)
        return True
    except Exception:
        logger.error(f"请求关闭通道失败，{traceback.format_exc()}")
        return False


def get_total_num(token, _type):
    fail_type = FAIL_TYPE_DICT.get(_type)
    # 定义基础URL
    url = "http://10.99.***"

    # 获取当前日期，避免多次调用
    if os.environ.get("debug") == "true":
        start_date = STATIC_DATE_START
        end_date = STATIC_DATE_END
    else:
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
    # 定义请求参数
    params = {
        "page": 1,
        "perPage": 15,
        "startDate": start_date,
        "failType": fail_type,
        "endDate": end_date,
        "field": "create_time",
        "order": "desc"
    }

    # 定义请求头
    headers = {
        "Host": "10.99.95.169",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "Resource-Id": "300041002",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "token": token,
        "Referer": "http://10.99.95.169*****",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }

    try:
        # 请求延时
        client = HTTPClient(retries=3, backoff_factor=1, timeout=30)
        # 发送GET请求
        response = client.get(caller_name=f'get_total_num_{_type}', url=url, headers=headers, params=params)
        # 解析JSON数据
        json_data = response.json()
        # 返回totalNum，若不存在则返回0
        total_num = json_data.get('data', {}).get('totalNum', 0)
        if total_num == 0:
            return 0, []
        else:
            return total_num, json_data.get('data').get('result', [])
    except Exception:
        logger.error(f"请求查询X/Y失败: {traceback.format_exc()}")
        return False


# 读取配置文件
def get_recipients_from_config():
    config = configparser.ConfigParser()

    # 关键修改：优先从 exe 所在目录读取配置
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  # exe所在目录
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(base_path, 'config.ini')

    # 强制检查外部配置文件是否存在
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"外部配置文件不存在: {config_path}")

    config.read(config_path, encoding='utf-8')

    # 获取当前时间的小时
    current_hour = datetime.now().hour

    # 根据时间段选择收件人
    if 7 <= current_hour < 17:
        recipients = config.get('daytime', 'recipients').split(',')
    else:
        recipients = config.get('nighttime', 'recipients').split(',')

    return [recipient.strip() for recipient in recipients]

def send_email(to_addrs, subject, message):
    from_addr = "qr_code.com"
    password = "*****"
    for to_addr in to_addrs:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        des_msg = html_message.format(STYLE, message)
        # 使用 MIMEText 来发送 HTML 格式的邮件内容
        msg.attach(MIMEText(des_msg, 'html'))

        try:
            # 连接到 SMTP 服务器
            server = smtplib.SMTP('****', 587)
            server.starttls()  # 启动 TLS 加密
            server.login(from_addr, password)  # 登录邮箱
            text = msg.as_string()  # 邮件内容转化为字符串
            server.sendmail(from_addr, to_addr, text)  # 发送邮件
            server.quit()  # 退出服务器
            logger.info(f"邮件发送成功，收件人：{to_addr} 主题：{subject}")
        except Exception:
            logger.error(f"邮件发送失败: {traceback.format_exc()}")


def combine_msg(token, fail_reason, fail_code, data_list):
    _data = query_b(token=token, fail_code=fail_code)
    if not _data:
        logger.warning(f"查询行业调控系统失败，fail_code: {fail_code}")
        return
    serial_num_old = _data.get('serialnumOld', '')
    if not serial_num_old:
        logger.warning(f"serial_num_old 为空，fail_code: {fail_code}")
        return
    with lock:
        if serial_num_old in processed_serials:
            return
        processed_serials.add(serial_num_old)
    produce_time = _data['produceTime']
    machine_name = _data['machineName']
    group_name = _data['groupName']
    brand = _data['brand']
    seq_num = _data['seqnum']
    msg_body = html_message_body.format(
        fail_reason, fail_code, serial_num_old, produce_time,
        machine_name, group_name, brand, seq_num
    )
    data_list.append(msg_body)


def get_alert_message_x(token, data):
    data_list = []
    for d in data:
        failCode = d['failCode']
        failReason = d['failReason']
        combine_msg(token=token, fail_reason=failReason, fail_code=failCode, data_list=data_list)
    return data_list


def get_alert_message_y(token, data):
    data_list = []
    for d in data:
        failCode = d['failCode']
        failReason = d['failReason']
        combine_msg(token=token, fail_reason=failReason, fail_code=failCode, data_list=data_list)
    return data_list


def get_alert_message(token, _type, data):
    """
        查询延时，行业调控回送有延时 需要手动等待
        """
    time.sleep(300)
    if _type == "x":
        return get_alert_message_x(token, data)
    elif _type == "y":
        return get_alert_message_y(token, data)
    else:
        raise ModuleNotFoundError("未知类型")


def handle_z_above_400(z, token):
    """
    处理 z 大于 400 的逻辑，例如触发 GET 请求等。
    """
    logger.info(f"Z指标超过400，执行关闭逻辑，当前值：{z}")
    # 执行 GET 请求或其他相关操作
    return get_request_to_shutdown(token)


if __name__ == '__main__':
    send_email(["pengbowen9112@qq.com"], "ddd", "测试")
