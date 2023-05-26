
from usr.dtu import DTU, get_current_app
from usr.logging import getLogger

logger = getLogger(__name__)


def create_app(config_path):
    dtu = DTU()
    dtu.setup(config_path)
    return dtu


app = create_app(config_path='/usr/dtu_config.json')


# 订阅主题并设定处理函数
@app.before_down('/public/TEST/upgrade/plan')
def upgrade(data):
    logger.info('route get data: ', data)
    return b'1234567890'


if __name__ == '__main__':
    app.run()
