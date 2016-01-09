from datetime import date
from unittest import skip

from demo.models import Group
from demo.core import db

from tests.base import DemoTest

BASE_URL = 'api/groups'
TEST_GROUPS = (('admin', 'admin group'), ('client', 'clients group'),
               ('employee', 'group for employees'))

GROUP_NOT_FOUND =  dict(success=False, message='Group not found.', status=404)
GROUP_CONFLICT = dict(success=False, message='A group with that name already exists.',
                      status=409)


class TestGroupApi(DemoTest):

    def test_get_group(self):
        """Test Group retrieval"""
        # Check that error message is returned if Group does not exist
        response = self.client.get(BASE_URL + '/{}'.format(1))
        self.assert404(response)

        group = self.create_group()
        response = self.client.get(BASE_URL + '/{}'.format(group.id))
        self.assert200(response)
        self.assertEquals(response.json['group'],
                          dict(date_created=str(date.today()),
                               description=group.description,
                               name=group.name,
                               user_ids=[],
                               id=group.id))

    def test_create_group(self):
        """Test Group creation"""
        test_name = 'Test Group'
        test_description = 'A test group'
        response = self.client.post(BASE_URL,
                                    data=dict(name=test_name,
                                              description=test_description))

        self.assertTrue(DemoTest.check_content_type(response))
        self.assertTrue(response.json['success'] == True)

        group = Group.query.filter_by(name=test_name).first()
        self.assertEquals(group.description, test_description)
        self.assertEquals(group.date_created, date.today())

        # Test that trying to create a Group with existing name results in error
        response = self.client.post(BASE_URL,
                                    data=dict(name=test_name,
                                              description=test_description))
        self.assertStatus(response, 409)
        self.assertEquals(response.json, GROUP_CONFLICT)

    def test_delete_group(self):
        """Test deleting a Group"""
        group = self.create_group()

        response = self.client.delete(BASE_URL + '/{}'.format(group.id))
        self.assertStatus(response, 200)
        self.assertTrue(response.json['success'] == True)
        self.assertIsNone(Group.query.get(group.id))

        # Test deleting a grroup that does not exists results in error
        response = self.client.delete(BASE_URL + '/{}'.format(group.id))
        self.assertStatus(response, 404)
        self.assertEquals(response.json, GROUP_NOT_FOUND)

    def test_modify_group(self):
        """Test modifying an existing Group"""
        test_name = 'Test Group'
        test_description = 'A test group'

        # Test modifying a Group that does not exists results in error
        response = self.client.put(BASE_URL + '/{}'.format(214),
                                   data=dict(name=test_name, description='new desc'))
        self.assertStatus(response, 404)
        self.assertEquals(response.json, GROUP_NOT_FOUND)

        group = self.create_group(name=test_name, description=test_description)
        response = self.client.put(BASE_URL + '/{}'.format(group.id),
                                   data=dict(name='new_name', description='new desc'))

        self.assertTrue(response.json['success'] == True)
        group = Group.query.get(group.id)
        self.assertEquals(group.description, 'new desc')
        self.assertEquals(group.name, 'new_name')

        # Test modifying a group to have a name that already exists results in error
        group = self.create_group()
        response = self.client.put(BASE_URL + '/{}'.format(group.id),
                                   data=dict(name='new_name', description='new desc'))
        self.assertEquals(response.json, GROUP_CONFLICT)

    def test_all_groups_are_returned_in_alphabetical_order(self):
        """Test all groups are returned"""
        groups = [self.create_group(name=test_group[0], description=test_group[1])
                  for test_group in TEST_GROUPS]

        response = self.client.get(BASE_URL)
        self.assertEqual(response.json['groups'][0]['id'], groups[0].id)
        self.assertEqual(response.json['groups'][1]['id'], groups[1].id)
        self.assertEqual(response.json['groups'][2]['id'], groups[2].id)

    def test_get_all_users_of_group(self):
        """Test that all Users in a Group are returned in alphabetical order"""
        # Test that error is thrown if group does not exist
        response = self.client.get(BASE_URL + '/{}/users'.format(1))
        self.assert404(response)

        user1 = self.create_user(name='Alpha Bravo', email='alpha@gmail.com')
        user2 = self.create_user(name='Zelda Charlie', email='zelda@gmail.com')
        group = self.create_group()
        user1.groups.append(group)
        user2.groups.append(group)
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        response = self.client.get(BASE_URL + '/{}/users'.format(group.id))
        self.assertEqual(response.json['users'][0]['name'], user1.name)
        self.assertEqual(response.json['users'][1]['name'], user2.name)

    def test_get_group_user_counts(self):
        """Tests that a list of Groups can be retrieved along with the number of
        groups they are members of in ascending order of user membership count"""
        user1 = self.create_user(name='Alpha Bravo', email='alpha@gmail.com')
        user2 = self.create_user(name='Zelda Charlie', email='zelda@gmail.com')
        group1 = self.create_group(name='Alpha', description='First Description')
        group2 = self.create_group(name='Beta', description='Second Description')

        user1.groups.append(group1)  # Only one membership, so group1 should appear first
        user1.groups.append(group2)
        user2.groups.append(group2)

        db.session.add(user1, user2)
        db.session.commit()

        response = self.client.get(BASE_URL + '/user_counts')
        self.assertEqual(response.json['groups'][0]['name'], group1.name)
        self.assertEqual(response.json['groups'][0]['user_count'], 1)
        self.assertEqual(response.json['groups'][1]['name'], group2.name)
        self.assertEqual(response.json['groups'][1]['user_count'], 2)
