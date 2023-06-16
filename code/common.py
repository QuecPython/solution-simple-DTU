import _thread


class Waiter(object):

    def __init__(self):
        self.__info = None  # usr information for notifier

        self.__lock = _thread.allocate_lock()
        self.__lock.acquire()  # acquire immediately for holding the lock.

        self.acquire = self.__lock.acquire
        self.release = self.__lock.release

    @property
    def info(self):
        return self.__info

    @info.setter
    def info(self, info):
        self.__info = info


class Condition(object):
    """条件变量(使用互斥锁实现)"""

    def __init__(self):
        self.__lock = _thread.allocate_lock()
        self.__waiters = []

    def __create_waiter(self):
        waiter = Waiter()
        with self.__lock:
            self.__waiters.append(waiter)
        return waiter

    def wait(self):
        waiter = self.__create_waiter()
        waiter.acquire()  # block here, waiting for release in the future.
        return waiter.info

    def notify(self, n=1, info=None):
        with self.__lock:
            for waiter in self.__waiters[:n]:
                waiter.info = info
                waiter.release()  # release here, some `wait` method will be unblocked.
                self.__waiters.remove(waiter)

    def notify_all(self, info=None):
        self.notify(n=len(self.__waiters), info=info)


class Event(object):

    def __init__(self):
        self.__lock = _thread.allocate_lock()
        self.flag = False
        self.cond = Condition()

    def wait(self):
        if self.flag is not True:
            self.cond.wait()
        return self.flag

    def set(self):
        with self.__lock:
            self.flag = True
            self.cond.notify_all()

    def clear(self):
        with self.__lock:
            self.flag = False

    def is_set(self):
        return self.flag
