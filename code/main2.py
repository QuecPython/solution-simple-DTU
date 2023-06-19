
from usr.dtu import DTU
from usr.settings import ConfigureHandler


def create_app(config_path):
    config = ConfigureHandler(config_path)
    dtu = DTU(config)
    return dtu


app = create_app('/usr/dtu_config.json')


if __name__ == '__main__':
    app.run()
