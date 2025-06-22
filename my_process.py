#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
@Time    : 2025/1/9 10:31
@File    : my_process.py
@Software: PyCharm
"""
import configparser
import datetime
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text

from common import send_email, get_total_num, get_recipients_from_config, get_total_num_for_z, get_alert_message, \
    handle_z_above_400
from controller import send_alert
from login import loginA, loginB
from model import MonitorRecord, db, get_latest_record_by_type
from my_logger import Logger

log = Logger(log_name="monitor")
logger = log.get_logger()

z_state = {'has_triggered': False, 'last_z_below_200': False}


class DataProcessor:
    @staticmethod
    def update_realtime_monitor(app, _type, _value):
        with app.app_context():
            session = db.session()
            try:
                # 尝试查找是否已有记录
                query = text("SELECT * FROM realtime_monitor WHERE _type = :_type LIMIT 1")
                result = session.execute(query, {'_type': _type}).fetchone()

                if result:
                    # 如果记录存在，执行更新操作
                    update_query = text("""
                        UPDATE realtime_monitor 
                        SET _value = :_value, timestamp = :timestamp 
                        WHERE _type = :_type
                    """)
                    session.execute(update_query,
                                    {'_value': _value, 'timestamp': datetime.datetime.now(), '_type': _type})
                else:
                    # 如果记录不存在，执行插入操作
                    insert_query = text("""
                        INSERT INTO realtime_monitor (_type, _value, timestamp) 
                        VALUES (:_type, :_value, :timestamp)
                    """)
                    session.execute(insert_query,
                                    {'_type': _type, '_value': _value, 'timestamp': datetime.datetime.now()})

                # 提交事务
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"更新实时数据失败，异常：{e}")
            finally:
                session.close()

    @staticmethod
    def update_database(app, _type, _value, alert_message, alert=True):
        with app.app_context():
            session = db.session()
            try:
                new_record = MonitorRecord(
                    _type=_type,
                    _value=_value,
                    alert=alert,
                    alert_message=alert_message
                )
                session.add(new_record)
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"更新数据库失败，异常：{e}")
            finally:
                session.close()

    @staticmethod
    def process_x(x, last_x, result_x, token_b, recipients, app):
        DataProcessor.update_realtime_monitor(app=app, _type=0, _value=x)
        if x > last_x:
            send_alert('x')
            alert_message_x_data = get_alert_message(token_b, "x", result_x)
            for msg in alert_message_x_data:
                send_email(recipients, "监控告警-上报失败", msg)
                DataProcessor.update_database(app=app, _type=0, _value=x, alert_message=msg)

    @staticmethod
    def process_y(y, last_y, result_y, token_b, recipient, app):
        DataProcessor.update_realtime_monitor(app, _type=1, _value=y)
        if y > last_y:
            send_alert('y')
            alert_message_y_data = get_alert_message(token_b, "y", result_y)
            for msg in alert_message_y_data:
                send_email(recipient, "监控告警-关联失败", msg)
                DataProcessor.update_database(app, _type=1, _value=y, alert_message=msg)

    @staticmethod
    def process_z(z, token_a, recipient, app):
        DataProcessor.update_realtime_monitor(app=app, _type=2, _value=z)
        # 上报指标判断逻辑，测试可手动调整
        if z > 400:
            if not z_state['has_triggered'] or z_state['last_z_below_200']:
                send_alert('z')
                if handle_z_above_400("z", token_a):
                    z_state['has_triggered'] = True
                    z_state['last_z_below_200'] = False
                alert_message_z = f"当前上报值:{z}，大于400，已关闭上报通道。"
                send_email(recipient, "监控告警-上报数量超出设定值", alert_message_z)
                DataProcessor.update_database(app=app, _type=2, _value=z, alert_message=alert_message_z)
        elif z < 200:
            z_state['last_z_below_200'] = True

    @staticmethod
    def monitor_and_notify(app):
        with app.app_context():
            logger.info("正在运行……")
            latest_record_type_0 = get_latest_record_by_type(0)
            latest_record_type_1 = get_latest_record_by_type(1)
            last_x = latest_record_type_0 if latest_record_type_0 else 0
            last_y = latest_record_type_1 if latest_record_type_1 else 0

            token_a = loginA()
            recipients = get_recipients_from_config()
            #打印发送邮件是否正确
            #logger.info(recipients)
            x, result_x = get_total_num(token_a, 'x')
            y, result_y = get_total_num(token_a, 'y')
            z = get_total_num_for_z(token_a)
            logger.info(f"X值：{x}，Y值{y}，Z值：{z}")
            token_b = loginB()

            x_thread = threading.Thread(target=DataProcessor.process_x,
                                        args=(x, last_x, result_x, token_b, recipients, app))
            y_thread = threading.Thread(target=DataProcessor.process_y,
                                        args=(y, last_y, result_y, token_b, recipients, app))
            z_thread = threading.Thread(target=DataProcessor.process_z, args=(z, token_a, recipients, app))

            x_thread.start()
            y_thread.start()
            z_thread.start()

            x_thread.join()
            y_thread.join()
            z_thread.join()

    @staticmethod
    def start_scheduler(app):
        # 读取配置文件
        config = configparser.ConfigParser()
        config.read('config.ini')

        # 获取配置文件中的时间间隔（默认为60秒）
        interval_seconds = int(config.get('scheduler', 'interval_seconds', fallback=60))
        # 启动调度器
        scheduler = BackgroundScheduler()
        # 每60秒运行一次监控函数
        scheduler.add_job(func=DataProcessor.monitor_and_notify, trigger='interval', id='monitor_and_notify',
                          seconds=interval_seconds, args=[app], max_instances=1)
        scheduler.start()
        # 保证调度器可以在后台运行，不会阻塞主线程
        while True:
            pass
