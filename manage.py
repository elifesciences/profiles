from configobj import ConfigObj
from flask_script import Manager, Server, Shell

from profiles.factory import create_app

config = ConfigObj('app.cfg')

app = create_app(config)
manager = Manager(app)


def make_shell_context() -> dict:
    return dict(app=app)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('runserver', Server())

if __name__ == '__main__':
    manager.run()
