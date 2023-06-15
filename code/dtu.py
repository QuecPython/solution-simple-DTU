import _thread
from usr.serial import Serial
from usr.mqttIot import MqttIot
from usr.socketIot import SocketIot
from usr.settings import config
from usr.logging import getLogger


logger = getLogger(__name__)


class DTU(object):

    def __init__(self):
        self.serial = None
        self.cloud = None

    def setup(self):
        self.serial = Serial(**config.get('uart_config'))

        cloud_type = config.get('system_config.cloud')
        if cloud_type == "mqtt":
            mqtt_config = config.get('mqtt_private_cloud_config')
            self.cloud = MqttIot(
                mqtt_config['client_id'],
                mqtt_config['server'],
                port=mqtt_config['port'],
                user=mqtt_config['user'],
                password=mqtt_config['password'],
                keepalive=mqtt_config['keepalive'],
                clean_session=mqtt_config['clean_session'],
                qos=mqtt_config['qos'],
                subscribe_topic=mqtt_config['subscribe'],
                publish_topic=mqtt_config['publish']
            )
        elif cloud_type == "tcp":
            socket_config = config.get('socket_private_cloud_config')
            self.cloud = SocketIot(
                ip_type=socket_config['ip_type'],
                keep_alive=socket_config['keep_alive'],
                domain=socket_config['domain'],
                port=socket_config['port']
            )

    def run(self):
        self.cloud.init()
        # 启动下行数据处理线程
        self.__down_transaction()
        # 启动上行数据处理线程
        self.__up_transaction()

    def __down_transaction(self):
        logger.info('start down transaction worker thread {}.'.format(_thread.get_ident()))
        _thread.start_new_thread(self.down_transaction_handler, ())

    def down_transaction_handler(self):
        while True:
            topic, data = self.cloud.recv()
            logger.info('down transfer msg: {}'.format(data))
            self.serial.write(data)

    def __up_transaction(self):
        logger.info('start up transaction worker thread {}.'.format(_thread.get_ident()))
        _thread.start_new_thread(self.up_transaction_handler, ())

    def up_transaction_handler(self):
        while True:
            data = self.serial.read(1024, timeout=100)
            if data:
                logger.info('up transfer msg: {}'.format(data))
                self.cloud.send(data)