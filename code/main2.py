
from usr.dtu import DTU
from usr.logging import getLogger

logger = getLogger(__name__)


def create_app():
    dtu = DTU()
    dtu.setup()
    return dtu


app = create_app()


if __name__ == '__main__':
    app.run()
