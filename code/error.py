# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#     http://www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ujson


class Error(object):
    code = 0x00
    desc = 'base error description.'

    def __str__(self):
        return ujson.dumps({'code': self.code, 'desc': self.desc})

    def __repr__(self):
        return self.__str__()


class ConnectError(Error):
    code = 0x01
    desc = 'connect error.'


class SubscribeError(Error):
    code = 0x02
    desc = 'subscribe error.'


class ListenError(Error):
    code = 0x03
    desc = 'listen error.'


class PublishError(Error):
    code = 0x04
    desc = 'publish error.'


class NetworkError(Error):
    code = 0x05
    desc = 'network status error.'


class SetSocketOptError(Error):
    code = 0x06
    desc = 'set socket option error.'


class TCPSendError(Error):
    code = 0x07
    desc = 'tcp send data error.'
