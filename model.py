#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
@Time    : 2025/1/9 10:29
@File    : model.py.py
@Software: PyCharm
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# 创建一个数据库实例
db = SQLAlchemy()


class MonitorRecord(db.Model):
    __tablename__ = 'monitor_record'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.now().date, index=True)
    _type = db.Column(db.Integer, index=True)
    _value = db.Column(db.Integer)
    alert = db.Column(db.Boolean, default=False)
    alert_message = db.Column(db.String(4096))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now())

    @property
    def type(self):
        return self._type

    def to_dict(self):
        """
        将 MonitorRecord 实例转换为字典，用于 JSON 序列化。
        """
        return {
            'id': self.id,
            'date': self.timestamp.strftime('%Y-%m-%d') if self.timestamp else None,
            '_type': self._type,
            '_value': self._value,
            'alert': self.alert,
            'alert_message': self.alert_message,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }

    @property
    def value(self):
        return self._value


class RealtimeMonitor(db.Model):
    __tablename__ = 'realtime_monitor'
    id = db.Column(db.Integer, primary_key=True)
    _type = db.Column(db.Integer, index=True)
    _value = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def to_dict(self):
        return {
            '_type': self._type,
            '_value': self._value,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value


def get_latest_record_by_type(record_type):
    """
    获取指定类型的最新记录，使用显式的SQL语句查询
    """
    sql = text("SELECT _value FROM realtime_monitor WHERE _type = :record_type ORDER BY timestamp DESC LIMIT 1")
    result = db.session.execute(sql, {'record_type': record_type}).fetchone()
    return result[0] if result else None
