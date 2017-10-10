from flask_script import Command


class ClearCommand(Command):
    NAME = 'clear'

    def __init__(self, *repositories):
        super(ClearCommand, self).__init__()
        self.repositories = repositories

    # weird decoration made by the superclass that wraps this method
    # not going to lose sleep over this for now,
    # let's see whether we get more commands
    # and we keep flask_script in the long term
    # pylint: disable=method-hidden
    def run(self):
        for each in self.repositories:
            each.clear()
