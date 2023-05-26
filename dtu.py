import _thread
import ql_fs
from usr.serial import Serial
from usr.mqttIot import MqttIot
from usr.settings import Settings
from usr.logging import getLogger


logger = getLogger(__name__)


class Singleton(object):

    def __init__(self, cls):
        self.cls = cls
        self.instance = None
        self.__init_lock = _thread.allocate_lock()

    def __call__(self, *args, **kwargs):
        with self.__init_lock:
            if self.instance is None:
                self.instance = self.cls(*args, **kwargs)
            return self.instance

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return str(self.cls)


class Parser(object):

    @classmethod
    def load(cls, data):
        return b'topic'.decode(), b'data'


@Singleton
class DTU(object):

    def __init__(self):
        self.serial = None
        self.cloud = None
        self.before_down_hooks = {}  # 下行钩子
        self.before_up_hooks = {}  # 上行钩子

    def setup(self, config_path=''):
        # >>> 读取配置
        if not ql_fs.path_exists(config_path):
            print(config_path)
            raise Exception('config path not exists!')

        Settings.set_config_path(config_path)
        config = Settings.current_settings()
        # <<<

        # >>> 串口对象
        self.serial = Serial(**config.get('uart_config'))
        # <<<

        # >>> 云端对象
        mqtt_config = config.get('mqtt_private_cloud_config')
        self.cloud = MqttIot(
            mqtt_config['server'],
            mqtt_config['qos'],
            mqtt_config['port'],
            mqtt_config['clean_session'],
            mqtt_config['client_id'],
            user=mqtt_config['username'],
            pass_word=mqtt_config['password'],
            life_time=mqtt_config['keep_alive'],
            sub_topic_list=mqtt_config['subscribe'],
            pub_topic_list=mqtt_config['publish']
        )
        # <<<

    def run(self):
        # 设置订阅主题消息回调函数
        self.cloud.set_callback(self.__down_transaction)

        # 初始化云对象(连接、订阅、监听)
        if not self.cloud.init():
            raise Exception('cloud init failed.')

        # 启动上行数据处理线程
        self.__up_transaction()

    def __up_transaction(self):
        logger.info('start up transaction worker thread {}.'.format(_thread.get_ident()))
        _thread.start_new_thread(self.up_transaction_handler, ())

    def up_transaction_handler(self):
        while True:
            data = self.serial.read(1024, timeout=1000)
            if data:
                self.up_through_post_data(data)

    def up_through_post_data(self, data):
        self.cloud.through_post_data(
            data,
            self.cloud.pub_topic_list[0]  # at least one topic for through post
        )

    def __down_transaction(self, topic, data):
        logger.info('start down transaction worker thread {}.'.format(_thread.get_ident()))
        _thread.start_new_thread(self.down_transaction_handler, (topic.decode(), data.decode()))

    def down_transaction_handler(self, topic, data):
        handler = self.before_down_hooks.get(topic)
        if handler is not None:
            rv = handler(data)
            if isinstance(rv, (bytearray, bytes)):
                self.down_through_post_data(rv)
        else:
            self.down_through_post_data(data)  # 默认下行数据全部透传

    def down_through_post_data(self, data):
        logger.info('down through post data: {}'.format(data))
        self.serial.write(data)

    def before_down(self, topic):
        """装饰器，下行数据添加钩子函数"""
        def wrapper(fn):
            # 添加订阅主题
            self.cloud.add_subscribe_topics([topic])
            # 注册主题处理函数
            self.before_down_hooks[topic] = fn
            return fn
        return wrapper

    # TODO: 暂未使用
    def before_up(self, topic):
        """装饰器，上行数据添加钩子函数"""
        def wrapper(fn):
            self.before_up_hooks[topic] = fn
            return fn
        return wrapper


def get_current_app():
    return DTU()
