from usr.dtu import DTU
from usr.settings import ConfigureHandler


def create_app():
    config = ConfigureHandler('/usr/dtu_config.json')
    dtu = DTU(config)
    return dtu


app = create_app()


if __name__ == '__main__':
    app.run()
