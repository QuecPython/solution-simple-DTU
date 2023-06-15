
from usr.dtu import DTU
from usr.settings import ConfigureHandler
from usr.logging import getLogger

logger = getLogger(__name__)


def create_app():
    config = ConfigureHandler('/usr/dtu_config.json')
    dtu = DTU(config)
    return dtu


app = create_app()


if __name__ == '__main__':
    app.run()
