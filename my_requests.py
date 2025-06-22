#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
@Time    : 2025/1/4 17:02
@File    : my_requests.py
@Software: PyCharm
"""

import time
from typing import Optional, Any

import requests
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError

from my_logger import Logger

log = Logger(log_name=__name__)
logger = log.get_logger()


class HTTPClient:
    def __init__(self, retries: int = 3, backoff_factor: float = 0.3, timeout: int = 10):
        """
        初始化 HTTPClient，设置重试次数、退避因子和超时时间。
        :param retries: 最大重试次数
        :param backoff_factor: 退避因子（重试间隔的增量）
        :param timeout: 请求超时设置，单位为秒
        """
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout

    def _get_retry_delay(self, attempt: int) -> float:
        """
        计算每次重试的延迟时间，采用退避策略
        :param attempt: 当前重试的次数
        :return: 延迟时间（秒）
        """
        return self.backoff_factor * (2 ** (attempt - 1))

    @staticmethod
    def _handle_exception(exception: Exception):
        """
        处理请求过程中发生的异常并记录日志。
        :param exception: 异常对象
        """
        logger.error(f"请求发生异常: {exception}")

    @staticmethod
    def _check_response(response: requests.Response) -> Optional[Any]:
        """
        检查响应状态码，并处理可能的 HTTP 错误。
        :param response: requests 的响应对象
        :return: 响应内容，如果状态码非 2xx 会抛出异常
        """
        if response.status_code == 200:
            return response
        else:
            raise HTTPError(f"请求失败，HTTP 状态码: {response.status_code}, 响应内容: {response.text}")

    def _request(self, caller_name: str, method: str, url: str, **kwargs) -> Optional[Any]:
        """
        封装的请求方法，支持自动重试、异常处理及响应检查。
        :param method: HTTP 请求方法，如 'get' 或 'post'
        :param url: 请求的 URL
        :param kwargs: 其他请求参数（如 headers, data, json 等）
        :return: 请求成功的响应数据
        """

        attempt = 0
        while attempt <= self.retries:
            try:
                attempt += 1
                logger.info(f"调用者 {caller_name} - 正在尝试第 {attempt} 次请求 {method.upper()} {url}")

                # 根据请求方法调用相应的 requests 方法
                if method.lower() == 'get':
                    _response = requests.get(url, timeout=self.timeout, **kwargs)
                elif method.lower() == 'post':
                    _response = requests.post(url, timeout=self.timeout, **kwargs)
                else:
                    raise ValueError(f"不支持的请求方法: {method}")

                # 检查响应是否成功
                return self._check_response(_response)

            except (ConnectionError, Timeout) as e:
                self._handle_exception(e)
                if attempt <= self.retries:
                    delay = self._get_retry_delay(attempt)
                    logger.warning(f"请求失败，正在重试...（{attempt}/{self.retries}）")
                    time.sleep(delay)
                else:
                    logger.error(f"请求失败，达到最大重试次数：{self.retries}")
                    raise
            except HTTPError as e:
                self._handle_exception(e)
                raise
            except RequestException as e:
                self._handle_exception(e)
                raise
            except Exception as e:
                self._handle_exception(e)
                raise

    def get(self, caller_name: str, url: str, **kwargs) -> Optional[Any]:
        """
        封装的 GET 请求方法
        :param caller_name: 请求的 函数名
        :param url: 请求的 URL
        :param kwargs: 请求参数
        :return: 请求成功的响应数据
        """
        return self._request(caller_name, 'get', url, **kwargs)

    def post(self, caller_name: str, url: str, **kwargs) -> Optional[Any]:
        """
        封装的 POST 请求方法
        :param caller_name: 请求的 函数名
        :param url: 请求的 URL
        :param kwargs: 请求参数
        :return: 请求成功的响应数据
        """
        return self._request(caller_name, 'post', url, **kwargs)
