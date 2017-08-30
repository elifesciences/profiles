from flask_script import Manager, Server, Shell

from profiles import create_app

app = create_app()
manager = Manager(app)


def make_shell_context():
    return dict(app=app)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('runserver', Server())

if __name__ == '__main__':
    manager.run()
