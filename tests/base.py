import os

from flask.ext.testing import TestCase

from demo import create_app, db
from demo.models import User, Group

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class DemoTest(TestCase):
    """Base Class for testing app"""
    def create_app(self):
        """Required for Flask-Testing"""
        app = create_app(config_name='testing')
        return app

    def setUp(self):
        """Initialize Database"""
        db.create_all()

    def tearDown(self):
        """Drop all tables"""
        db.session.remove()
        db.drop_all()

    @staticmethod
    def check_content_type(response):
        """Verify content type is correct"""
        return response.headers['Content-Type'] == 'application/json'

    def create_user(self, name='John Smith', email='john@gmail.com'):
        """Creates a basic test user"""
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    def create_group(self, name='Test Group', description='Testing Group'):
        """Creates a basic test group"""
        group = Group(name=name, description=description)
        db.session.add(group)
        db.session.commit()
        return group


if __name__ == '__main__':
    pass

