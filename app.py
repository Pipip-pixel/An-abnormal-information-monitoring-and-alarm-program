#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
@Time    : 2025/1/9 10:36
@File    : app.py
@Software: PyCharm
"""
import threading
import traceback

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from controller import send_alert
from model import MonitorRecord, db, RealtimeMonitor
from my_logger import Logger
from my_process import DataProcessor

log = Logger(log_name='monitor_app')
logger = log.get_logger()


def create_app():
    app = Flask(__name__, template_folder="templates")
    CORS(app)

    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitor.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化数据库
    db.init_app(app)

    # 应用配置和路由注册
    @app.route('/get_current_values', methods=['GET'])
    def get_current_values():
        # 查询表中最新的 X, Y, Z 数据
        record = RealtimeMonitor.query.all()
        x = record[0].value
        y = record[1].value
        z = record[2].value

        # 返回这些数据
        return jsonify({
            'x': x if x else 0,
            'y': y if y else 0,
            'z': z if z else 0
        })

    @app.route('/monitor', methods=['GET', 'POST'])
    def monitor():
        if request.method == 'POST':
            records = MonitorRecord.query.filter(MonitorRecord.alert).order_by(MonitorRecord.id.desc()).all()
            records_dict = [record.to_dict() for record in records]
            return jsonify(records=records_dict)
        else:
            return render_template('monitor.html')

    @app.route('/', methods=['GET'])
    def index():
        return render_template('monitor.html')

    @app.route('/delete/<int:_id>', methods=['DELETE'])
    def delete_record(_id):
        try:
            record = MonitorRecord.query.get(_id)
            if record:
                db.session.delete(record)
                db.session.commit()
                return jsonify({'success': True})
            return jsonify({'error': 'Record not found'}), 404
        except Exception:
            logger.error(f"Error deleting record: {traceback.format_exc()}")
            return jsonify({'error': 'Server Error'}), 500

    @app.route('/reset', methods=['POST'])
    def reset_alert():
        try:
            send_alert('global')
            return jsonify({'success': True})
        except Exception:
            logger.error(f"Error resetting alert: {traceback.format_exc()}")
            return jsonify({'success': False})

    return app


if __name__ == '__main__':
    my_app = create_app()
    processor = DataProcessor()
    # 启动调度器的线程
    scheduler_thread = threading.Thread(target=processor.start_scheduler, args=[my_app])
    scheduler_thread.daemon = True
    scheduler_thread.start()
    # 启动Flask应用
    my_app.run(debug=False, use_reloader=False)
