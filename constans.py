#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/28 9:25
@File    : constans.py
@Software: PyCharm
"""
STATIC_DATE_START = "2024-07-01"
STATIC_DATE_END = "2024-07-01"
FAIL_TYPE_DICT = {
    "x": "FC04",
    "y": "FC01"
}
STYLE = """<style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            color: #333;
            margin: 0;
            padding: 20px;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        h2 {
            color: #4A90E2;
            text-align: center;
            font-size: 24px;
            margin-bottom: 15px;
        }
        .section-title {
            color: #333;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .info-box {
            background-color: #f2f8ff;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .info-box p {
            margin: 5px 0;
        }
        .highlight {
            color: #E94E77;
            font-weight: bold;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            text-align: center;
            border-radius: 5px;
            display: inline-block;
            text-decoration: none;
            font-weight: bold;
            margin-top: 10px;
        }
        .footer {
            font-size: 12px;
            color: #888;
            text-align: center;
            margin-top: 20px;
        }
        .footer a {
            color: #4A90E2;
            text-decoration: none;
        }
    </style>"""
# HTML 邮件内容
html_message = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>邮件告警</title>
    {}
</head>
<body>
    <div class="container">
        <h2>邮件告警通知</h2>

        {}

        <div class="footer">
            <p>本邮件由自动系统生成，请勿回复。</p>
        </div>
    </div>
</body>
</html>
"""

html_message_body = """
<div class="info-box">
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
</div>
"""
