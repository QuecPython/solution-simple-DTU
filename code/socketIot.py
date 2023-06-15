import usys
import utime
import _thread
import usocket
from queue import Queue
from usr.logging import getLogger

logger = getLogger(__name__)


class SocketIot(object):
    """This class is tcp socket"""

    def __init__(self, ip_type=None, protocol="TCP", keep_alive=None, domain=None, port=None):
        super().__init__()
        if protocol == "TCP" or protocol is None:
            self.__protocol = "TCP"
        else:
            self.__protocol = "UDP"
        if ip_type == "IPv6":
            self.__ip_type = usocket.AF_INET6
        else:
            self.__ip_type = usocket.AF_INET
        self.__port = port
        self.__domain = domain
        self.__addr = None
        self.__socket = None
        self.__socket_args = []
        self.__timeout = 50
        self.__keep_alive = keep_alive
        self.__listen_thread_id = None
        self.__init_addr()
        self.__init_socket()
        self.queue = Queue()

    def __init_addr(self):
        if self.__domain is not None:
            if self.__port is None:
                self.__port = 8883 if self.__domain.startswith("https://") else 1883
            try:
                addr_info = usocket.getaddrinfo(self.__domain, self.__port)
                self.__ip = addr_info[0][-1][0]
            except Exception as e:
                usys.print_exception(e)
                raise ValueError("Domain %s DNS parsing error. %s" % (self.__domain, str(e)))
        self.__addr = (self.__ip, self.__port)

    def __init_socket(self):
        if self.__protocol == 'TCP':
            socket_type = usocket.SOCK_STREAM
            socket_proto = usocket.IPPROTO_TCP
        elif self.__protocol == 'UDP':
            socket_type = usocket.SOCK_DGRAM
            socket_proto = usocket.IPPROTO_UDP
        else:
            raise ValueError("Args method is TCP or UDP, not %s" % self.__protocol)
        self.__socket_args = (self.__ip_type, socket_type, socket_proto)

    def __connect(self):
        if self.__socket_args:
            try:
                self.__socket = usocket.socket(*self.__socket_args)
                if self.__protocol == "TCP":
                    self.__socket.connect(self.__addr)
                return True
            except Exception as e:
                usys.print_exception(e)

        return False

    def __disconnect(self):
        if self.__socket is not None:
            try:
                self.__socket.close()
                self.__socket = None
                return True
            except Exception as e:
                usys.print_exception(e)
                return False
        else:
            return True

    def recv_thread_worker(self):
        """Read data by socket.
        """
        while True:
            data = b""
            try:
                if self.__socket is not None:
                    data = self.__socket.recv(1024)
            except Exception as e:
                if e.args[0] != 110:
                    logger.error("%s read failed. error: %s" % (self.__protocol, str(e)))
                    break
            else:
                if data != b"":
                    try:
                        self.queue.put((None, data))
                    except Exception as e:
                        logger.error("{}".format(e))
            utime.sleep_ms(50)

    def listen(self):
        self.__listen_thread_id = _thread.start_new_thread(self.recv_thread_worker, ())

    def init(self, enforce=False):
        if enforce is False:
            if self.get_status() == 0:
                return True
        if self.__socket is not None:
            try:
                self.__disconnect()
            except Exception as e:
                logger.error("tcp disconnect falied. %s" % e)
            try:
                if self.__listen_thread_id is not None:
                    _thread.stop_thread(self.__listen_thread_id)
            except Exception as e:
                logger.error("stop listen thread falied. %s" % e)

        # FIX: when connect failed we return False instead of raise Exception for another try(self.init when post data.)
        if not self.__connect():
            return False

        if self.__keep_alive != 0:
            try:
                self.__socket.setsockopt(usocket.SOL_SOCKET, usocket.TCP_KEEPALIVE, self.__keep_alive)
            except Exception as e:
                self.__socket.close()
                logger.error("socket option set error:", e)
                raise Exception("socket option set error")
        self.__socket.settimeout(self.__timeout)
        # Start receive socket data
        self.listen()
        logger.debug("self.get_status(): %s" % self.get_status())
        if self.get_status() == 0:
            return True
        else:
            return False

    def get_status(self):
        _status = -1
        if self.__socket is not None:
            try:
                if self.__protocol == "TCP":
                    socket_sta = self.__socket.getsocketsta()
                    if socket_sta in range(4):
                        # Connecting
                        _status = 1
                    elif socket_sta == 4:
                        # Connected
                        _status = 0
                    elif socket_sta in range(5, 11):
                        # Disconnect
                        _status = 2
                elif self.__protocol == "UDP":
                    _status = 0
            except Exception as e:
                usys.print_exception(e)
        return _status

    def send(self, data):
        if self.__socket is not None:
            try:
                write_data_num = self.__socket.write(data)
                if write_data_num == len(data):
                    return True
            except Exception as e:
                usys.print_exception(e)

        return False

    def recv(self):
        return self.queue.get()
