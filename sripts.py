#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
@Time    : 2025/1/6 11:57
@File    : scripts.py
@Software: PyCharm
"""
import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, Boolean, String, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 获取当前脚本所在的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'instance', 'monitor.db')

# 检查目录是否存在，如果不存在则创建
if not os.path.exists(os.path.dirname(db_path)):
    os.makedirs(os.path.dirname(db_path))

# SQLite 数据库 URI
DATABASE_URI = f'sqlite:///{db_path}'

# 创建 SQLAlchemy 引擎
engine = create_engine(DATABASE_URI, echo=True)

# 基类，所有模型将从它继承
Base = declarative_base()


# 定义 MonitorRecord 表
class MonitorRecord(Base):
    __tablename__ = 'monitor_record'
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=datetime.now().date, index=True)
    _type = Column(Integer, index=True)
    _value = Column(Integer)
    alert = Column(Boolean, default=False)
    alert_message = Column(String(4096))
    timestamp = Column(DateTime, default=lambda: datetime.now())

    def __repr__(self):
        return f"<MonitorRecord(id={self.id}, _type={self._type}, _value={self._value}, alert={self.alert})>"


# 定义 RealtimeMonitor 表
class RealtimeMonitor(Base):
    __tablename__ = 'realtime_monitor'
    id = Column(Integer, primary_key=True)
    _type = Column(Integer, index=True)
    _value = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return f"<RealtimeMonitor(id={self.id}, _type={self._type}, _value={self._value}, timestamp={self.timestamp})>"


# 创建所有表
def create_tables():
    Base.metadata.create_all(engine)
    print("所有表已成功创建！")


# 连接到数据库并执行相关操作
def get_session():
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == '__main__':
    # 创建数据库表
    # create_tables()

    # 示例：插入数据
    session = get_session()
    new_record1 = MonitorRecord(_type=0, _value=100, alert=True, alert_message="""<div class="info-box">
    <div class="section-title">问题件信息</div>
    <p><strong>失败原因:</strong>{0}</p>
    <p><strong>件码:</strong>{1}</p>
</div>

<div class="info-box">
    <div class="section-title">生产信息</div>
    <p><strong>32位件码:</strong> <span class="highlight">{2}</span></p>
    <p><strong>生产时间:</strong> <span class="highlight">{3}</span></p>
    <p><strong>机台:</strong> <span class="highlight">{4}</span></p>
    <p><strong>班次:</strong> <span class="highlight">{5}</span></p>
    <p><strong>牌号:</strong> <span class="highlight">{6}</span></p>
    <p><strong>顺序号:</strong> <span class="highlight">{7}</span></p>
</div>""")
    new_record2 = MonitorRecord(_type=1, _value=100, alert=True, alert_message="""<div class="info-box">
    <div class="section-title">问题件信息</div>
    <p><strong>失败原因:</strong>{0}</p>
    <p><strong>件码:</strong>{1}</p>
</div>

<div class="info-box">
    <div class="section-title">生产信息</div>
    <p><strong>32位件码:</strong> <span class="highlight">{2}</span></p>
    <p><strong>生产时间:</strong> <span class="highlight">{3}</span></p>
    <p><strong>机台:</strong> <span class="highlight">{4}</span></p>
    <p><strong>班次:</strong> <span class="highlight">{5}</span></p>
    <p><strong>牌号:</strong> <span class="highlight">{6}</span></p>
    <p><strong>顺序号:</strong> <span class="highlight">{7}</span></p>
</div>""")
    new_record3 = MonitorRecord(_type=2, _value=500, alert=True, alert_message="Z大于400！")
    session.add(new_record1)
    session.add(new_record2)
    session.add(new_record3)
    session.commit()

    # 查询并打印所有记录
    # records = session.query(MonitorRecord).all()
    # for record in records:
    #     print(record)

    # 关闭会话
    # session.close()
