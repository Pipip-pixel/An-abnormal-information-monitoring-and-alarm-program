import configparser
import time
import traceback

import serial

from my_logger import Logger

log = Logger(log_name=__name__)
logger = log.get_logger()


class LampController:
    # 定义操作功能和灯的地址映射
    OPERATIONS = {
        '关闭': 0x00,
        '打开': 0x02,
        '闪烁': 0x03
    }
    ADDRESSES = {
        '黄灯': 0x01,
        '绿灯': 0x02,
        '红灯': 0x03,
        '蜂鸣': 0x04,
        '黄灯+蜂鸣': 0x05,
        '绿灯+蜂鸣': 0x06,
        '红灯+蜂鸣': 0x07,
        '全局': 0x00
    }

    def __init__(self, start_address=0xA0):
        """
        初始化LampController实例，设置默认的起始地址（如0xA0）
        """
        self.start_address = start_address

    def calculate_checksum(self, address, operation):
        """
        计算校验和：校验和是起始地址、操作地址、操作码之和
        校验和 = (起始地址 + 地址 + 操作码) & 0xFF（即取低8位）
        """
        checksum = (self.start_address + address + operation) & 0xFF
        return checksum

    def generate_command(self, operation_name, address_name):
        """
        生成完整的命令，包括起始地址、操作地址、操作码和校验和
        """
        if operation_name not in self.OPERATIONS:
            raise ValueError(f"未知的操作: {operation_name}")
        if address_name not in self.ADDRESSES:
            raise ValueError(f"未知的地址: {address_name}")
        # 获取操作码和地址
        operation_code = self.OPERATIONS[operation_name]
        address_code = self.ADDRESSES[address_name]
        # 计算校验和
        checksum = self.calculate_checksum(address_code, operation_code)
        # 返回最终命令
        command = [self.start_address, address_code, operation_code, checksum]
        return command

    def execute(self, operation_name, address_name, port, baudrate, timeout):
        """
        执行操作，生成命令并通过串口发送，检查是否成功
        """
        command = self.generate_command(operation_name, address_name)
        logger.info(f"生成命令并发送: {command}")
        try:
            # 打开串口连接
            ser = serial.Serial(port, baudrate, timeout=timeout)
            # 发送命令到串口
            ser.write(bytes(command))
            # 等待设备反馈（例如等待一段时间，设备返回确认消息）
            time.sleep(1)
            # 假设设备会返回一个响应，读取串口数据
            response = ser.readline()
            # 如果设备返回的数据是字节序列，尝试进行解码
            if response:
                if b'\xa0' in response:
                    logger.info(f"设备返回: {response}")
                    return True
                else:
                    logger.error(f"设备返回非预期：{response}")
                    return False
            else:
                logger.error("没有收到设备反馈")
                return False
        except Exception as e:
            logger.error(f"发生异常: {e}")
            return False

    def control_lamp(self, lamp_name, operation_name, port, baudrate, timeout):
        """
        控制指定灯的操作，简化调用接口。
        传入灯名称和操作名称，自动生成并执行命令
        """
        if lamp_name not in self.ADDRESSES:
            raise ValueError(f"未知的灯名称: {lamp_name}")
        if operation_name not in self.OPERATIONS:
            raise ValueError(f"未知的操作: {operation_name}")
        return self.execute(operation_name, lamp_name, port, baudrate, timeout)


def send_alert(_type):
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    # 获取串口配置
    port = config['serial'].get('port', 'COM3')
    baudrate = int(config['serial'].get('baudrate', '9600'))
    timeout = int(config['serial'].get('timeout', '1'))

    # 创建灯控制器对象
    controller = LampController()
    try:
        # 获取配置类型，执行相应的灯控制操作
        if _type in config:
            lamp_name = config[_type].get('lamp', '未定义灯')
            operation = config[_type].get('operation', '未定义操作')
            controller.control_lamp(lamp_name, operation, port, baudrate, timeout)
        else:
            logger.error(f"未找到配置类型: {_type}")
    except Exception:
        logger.error(f"告警失败：{traceback.format_exc()}")


# 测试工具类
if __name__ == '__main__':
    send_alert('x')
    send_alert('y')
    send_alert('z')
    send_alert('global')
