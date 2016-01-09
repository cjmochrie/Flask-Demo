from datetime import date
from unittest import skip

from demo.models import User
from demo.core import db

from tests.base import DemoTest

BASE_URL = '/api/users'
TEST_USERS = (('john', 'john@gmail.com'), ('mary', 'mary@gmail.com'), ('alan', 'al@gmail.com'))

USER_NOT_FOUND =  dict(success=False, message='User not found.', status=404)
USER_CONFLICT = dict(success=False, message='A user with that email already exists.', status=409)

class TestUserApi(DemoTest):
    def test_get_user(self):
        """Test user retrieval"""
        response = self.client.get(BASE_URL + '/{}'.format(1))
        self.assert404(response)

        user = self.create_user()

        response = self.client.get(BASE_URL + '/{}'.format(user.id))
        self.assert200(response)
        self.assertEquals(response.json['user'],
                          dict(date_created=str(date.today()),
                               email=user.email,
                               name=user.name,
                               group_ids=[],
                               id=user.id))

    def test_create_user(self):
        """Test User creation"""
        test_email = 'test_user_1@gmail.com'
        test_name = 'Test User'
        response = self.client.post(BASE_URL, data=dict(email=test_email, name=test_name))

        self.assertTrue(TestUserApi.check_content_type(response))
        self.assertTrue(response.json['success'] == True)

        user = User.query.filter_by(email=test_email).first()
        self.assertEquals(user.email, test_email)
        self.assertEquals(user.name, test_name)
        self.assertEquals(user.date_created, date.today())

        # Test that creating a user with existing email results in error
        response = self.client.post(BASE_URL, data=dict(email=test_email, name=test_name))
        self.assertStatus(response, 409)
        self.assertEquals(response.json, USER_CONFLICT)

    def test_delete_user(self):
        """Test User deletion"""
        user = self.create_user()

        response = self.client.delete(BASE_URL + '/{}'.format(user.id))
        self.assertEquals(response.json, dict(success=True))

        # Test deleting a user that does not exists results in error
        response = self.client.delete(BASE_URL + '/{}'.format(user.id))
        self.assertStatus(response, 404)
        self.assertEquals(response.json, USER_NOT_FOUND)

    def test_modify_user(self):
        """Test user can be modified"""
        test_email = 'test_user_1@gmail.com'
        test_name = 'Test User'

        # Test modifying a user that does not exists results in error
        response = self.client.put(BASE_URL + '/{}'.format(123),
                                   data=dict(email=test_email, name='new name'))
        self.assertStatus(response, 404)
        self.assertEquals(response.json, USER_NOT_FOUND)

        user = self.create_user(test_name, test_email)
        response = self.client.put(BASE_URL + '/{}'.format(user.id),
                                   data=dict(email='new_email', name='new name'))

        self.assertTrue(response.json['success'] == True)
        self.assertEquals(user.name, 'new name')
        self.assertEquals(user.email, 'new_email')

        # Test modifying a User to have an email already in existence results in error
        user2 = self.create_user(name='abc', email='doesntmatter')
        response = self.client.put(BASE_URL + '/{}'.format(user2.id),
                                   data=dict(email='new_email', name='new name'))
        self.assertEquals(response.json, USER_CONFLICT)


    def test_all_users_are_returned_in_alphabetical_order(self):
        """Test all users are returned"""
        users = [self.create_user(name=test_user[0], email=test_user[1])
                 for test_user in TEST_USERS]

        response = self.client.get(BASE_URL)
        self.assertEqual(response.json['users'][0]['id'], users[2].id)
        self.assertEqual(response.json['users'][1]['id'], users[0].id)
        self.assertEqual(response.json['users'][2]['id'], users[1].id)

    def test_add_user_to_group(self):
        """Tests that a user can be added to a group"""
        # First test that errors are thrown correctly
        response = self.client.put(BASE_URL + '/{}/groups'.format(1),
                                   data=dict(group_id=1))
        self.assert404(response)
        user = self.create_user()

        response = self.client.put(BASE_URL + '/{}/groups'.format(user.id),
                                   data=dict(group_id=1))
        self.assert404(response)

        group = self.create_group()

        response = self.client.put(BASE_URL + '/{}/groups'.format(user.id),
                                   data=dict(group_id=group.id))

        self.assertEqual(response.json['user']['group_ids'][0], group.id)
        self.assertEqual(group.users[0], user)
        self.assertEqual(user.groups[0], group)

    def test_remove_user_from_group(self):
        """Tests that a user can be removed from a group"""
        # First test that errors are thrown correctly
        response = self.client.delete(BASE_URL + '/{}/groups'.format(1),
                                   data=dict(group_id=1))
        self.assert404(response)
        user = self.create_user()

        response = self.client.delete(BASE_URL + '/{}/groups'.format(user.id),
                                   data=dict(group_id=1))
        self.assert404(response)

        group = self.create_group()
        user.groups.append(group)
        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.groups[0], group)

        response = self.client.delete(BASE_URL + '/{}/groups'.format(user.id),
                                      data=dict(group_id=group.id))

        self.assertEqual(response.json['user']['group_ids'], [])
        self.assertEqual(group.users, [])
        self.assertEqual(user.groups, [])

    def test_get_users_groups(self):
        """Tests that all user's groups are returned in alphabetical order"""
        response = self.client.get(BASE_URL + '/{}/groups'.format(1))
        self.assert404(response)

        user = self.create_user()
        group1 = self.create_group(name='Alpha', description='First Description')
        user.groups.append(group1)
        group2 = self.create_group(name='Beta', description='Second Description')
        user.groups.append(group2)
        db.session.add(user)
        db.session.commit()

        response = self.client.get(BASE_URL + '/{}/groups'.format(user.id))
        self.assertEqual(response.json['groups'][0]['name'], group1.name)
        self.assertEqual(response.json['groups'][1]['name'], group2.name)

    def test_get_user_group_counts(self):
        """Tests that a list of Users can be retrieved along with the number of
        groups they are members of in ascending order of group membership count"""
        user1 = self.create_user(name='Alpha Bravo', email='alpha@gmail.com')
        user2 = self.create_user(name='Zelda Charlie', email='zelda@gmail.com')
        group1 = self.create_group(name='Alpha', description='First Description')
        group2 = self.create_group(name='Beta', description='Second Description')

        user1.groups.append(group1)
        user1.groups.append(group2)
        user2.groups.append(group2)  # Only one membership, so user1 should appear second

        db.session.add(user1, user2)
        db.session.commit()

        response = self.client.get(BASE_URL + '/group_counts')
        self.assertEqual(response.json['users'][1]['name'], user1.name)
        self.assertEqual(response.json['users'][1]['group_count'], 2)
        self.assertEqual(response.json['users'][0]['name'], user2.name)
        self.assertEqual(response.json['users'][0]['group_count'], 1)
