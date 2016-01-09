from flask_restful import Api, Resource
from webargs.flaskparser import use_kwargs
from webargs import fields
from flask import Blueprint

from ..services import user_service, group_service
from ..errors import errors
from ..schemas import user_schema, users_schema, groups_schema

users_bp = Blueprint('user_bp', __name__)
api = Api(users_bp, errors=errors)

user_update = {'email': fields.Str(required=True), 'name': fields.Str(required=True)}

class Users(Resource):
    """List existing users and create new users"""
    def get(self):
        """List all Users Sorted alphabetically"""
        users = user_service.all('name')
        result = users_schema.dump(users)
        return {'success': True, 'users': result.data}, 200

    @use_kwargs(user_update)
    def post(self, email, name):
        """Create a new user"""
        user = user_service.new(name=name, email=email)
        result = user_schema.dump(user)
        return {'success': True, 'user': result.data}, 200


class UserManagement(Resource):
    """Get, update and delete existing User models"""
    def get(self, id):
        """Return user"""
        user = user_service.get_or_404(id)
        result = user_schema.dump(user)
        return {'success': True, 'user': result.data}, 200

    def delete(self, id):
        """Delete a user"""
        user = user_service.get_or_404(id)
        user_service.delete(user)
        return {'success': True}, 200

    @use_kwargs(user_update)
    def put(self, id, email, name):
        """Modify an existing user"""
        user = user_service.get_or_404(id)
        user = user_service.update(user, email=email, name=name)
        result = user_schema.dump(user)
        return {'success': True, 'user': result.data}, 200


class UserGroups(Resource):
    """Resource for listing and managing User Group memberships"""
    def get(self, id):
        """Return a list of the User's Group memberships"""
        user = user_service.get_or_404(id)
        result = groups_schema.dump(user.groups)
        return {'success': True, 'groups': result.data}, 200

    @use_kwargs({'group_id': fields.Integer(required=True)})
    def put(self, id, group_id):
        """Add a Group to the User's Group memberships"""
        user = user_service.get_or_404(id)
        group = group_service.get_or_404(group_id)
        user.groups.append(group)
        user_service.save(user)

        result = user_schema.dump(user)
        return {'success': True, 'user': result.data}, 200

    @use_kwargs({'group_id': fields.Integer(required=True)})
    def delete(self, id, group_id):
        """Remove a Group from the User's Group memberships"""
        user = user_service.get_or_404(id)
        group = group_service.get_or_404(id)
        user.groups.remove(group)
        user_service.save(user)

        result = user_schema.dump(user)
        return {'success': True, 'user': result.data}, 200


class UserGroupCounts(Resource):
    def get(self):
        """Returns a list of Users sorted by the number of Groups they are members
        of (ascending) along with a count of the groups"""
        users = user_service.all()
        users.sort(key=lambda x: len(x.groups))
        results = [{'name': user.name, 'id': user.id, 'group_count': len(user.groups)}
                   for user in users]
        return {'success': True, 'users': results}, 200


api.add_resource(Users, '')
api.add_resource(UserGroupCounts, '/group_counts')
api.add_resource(UserManagement, '/<int:id>')
api.add_resource(UserGroups, '/<int:id>/groups')
