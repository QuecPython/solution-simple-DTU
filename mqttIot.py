
import utime
import _thread
from umqtt import MQTTClient
from usr.logging import getLogger


log = getLogger(__name__)


class MqttIot(object):
    def __init__(self, server, qos, port, clean_session,
                 client_id, user="", pass_word="", life_time=120,
                 sub_topic_list=None, pub_topic_list=None, callback=None):

        self.__pk = None
        self.__ps = None
        self.__dk = user
        self.__ds = None
        self.__server = server
        self.__qos = qos
        self.__port = port
        self.__mqtt = None
        self.__clean_session = clean_session
        self.__life_time = life_time
        self.__client_id = client_id
        self.__password = pass_word

        self.__cb = callback or self.sub_cb
        self.sub_topic_list = sub_topic_list or []
        self.pub_topic_list = pub_topic_list or []

    def __subscribe_topic(self):
        for usr_sub_topic in self.sub_topic_list:
            if self.__mqtt.subscribe(usr_sub_topic, qos=0) == -1:
                log.error("Topic [%s] Subscribe Failed." % usr_sub_topic)

    def add_subscribe_topics(self, topics):
        self.sub_topic_list.extend(topics)

    def sub_cb(self, topic, data):
        raise NotImplementedError('you must implemented self.sub_cb or set a custom callback.')

    def set_callback(self, cb):
        self.__cb = cb

    def __listen(self):
        while True:
            self.__mqtt.wait_msg()
            utime.sleep_ms(100)

    def __start_listen(self):
        _thread.start_new_thread(self.__listen, ())

    def init(self):
        log.debug(
            "mqtt init. self.__client_id: {}, self.__password: {}, self.__dk: {}, self.__ds: {}".format(
                self.__client_id, self.__password, self.__dk, self.__ds
            )
        )

        self.__mqtt = MQTTClient(
            client_id=self.__client_id,
            server=self.__server,
            port=self.__port,
            user=self.__dk,
            password=self.__password,
            keepalive=self.__life_time,
            ssl=False
        )

        try:
            self.__mqtt.connect(clean_session=self.__clean_session)
        except Exception as e:
            log.error("mqtt connect error: %s" % e)
        else:
            self.__mqtt.set_callback(self.__cb)
            self.__subscribe_topic()
            self.__start_listen()
            log.debug("mqtt start.")

        log.debug("mqtt status: %s" % self.get_status())
        if self.get_status():
            return True
        else:
            return False

    def close(self):
        self.__mqtt.disconnect()

    def get_status(self):
        try:
            return True if self.__mqtt.get_mqttsta() == 0 else False
        except Exception:
            return False
    
    def through_post_data(self, data, topic):
        try:
            self.__mqtt.publish(topic, data, self.__qos)
        except Exception:
            log.error("mqtt publish topic %s failed. data: %s" % (topic, data))
            return False
        else:
            return True
