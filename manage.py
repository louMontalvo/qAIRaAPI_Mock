import os
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from qairamap.main import create_app, db

#we created initially to create the application instance with the required parameter 
#from the environment variable which can be either of the following
app = create_app(os.getenv('BOILERPLATE_ENV') or 'dev')

app.app_context().push()
#instantiates the manager class by passing the app instance to their respective constructors.
manager = Manager(app)
#instantiates the migrate class by passing the app instance to their respective constructors.
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def run():
    app.run()

@manager.command
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('qairamap/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    manager.run()