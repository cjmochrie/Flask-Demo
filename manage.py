#!/usr/bin/env python
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='demo/*')
    COV.start()

from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand

from demo import create_app, db, models

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
if os.getenv('MINIFY_JSON') == 'true':
    app.config['RESTFUL_JSON'] = {'separators': (',',':'),
                                  'indent': None,
                                  'sort_keys': False}

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, models=models)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(host="0.0.0.0", port=8000))

@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest

    tests = unittest.TestLoader().discover('tests')

    unittest.TextTestRunner(verbosity=2).run(tests)
    if coverage and COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

if __name__ == '__main__':
    manager.run()

# Above code cribbed from https://github.com/miguelgrinberg/flasky-with-celery/blob/master/manage.py