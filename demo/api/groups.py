from flask import Blueprint
import flask_restful
from flask_restful import Api, Resource
from webargs.flaskparser import use_kwargs
from webargs import fields, missing

from ..services import group_service
from ..errors import errors
from ..schemas import groups_schema, group_schema, users_schema

groups_bp = Blueprint('groups_bp', __name__)
api = Api(groups_bp, errors=errors)


group_update = {'name': fields.Str(required=True), 'description': fields.Str()}


class Groups(Resource):
    """Listing and creating Groups"""
    def get(self):
        """List all Groups alphabetically"""
        groups = group_service.all('name')
        result = groups_schema.dump(groups)
        return {'success': True, 'groups': result.data}, 200

    @use_kwargs(group_update)
    def post(self, name, description=None):
        """Create a new group, return error if already exists"""
        if description is missing:
            description=None
        group = group_service.new(name=name, description=description)
        result = group_schema.dump(group)
        return {'success': True, 'group': result.data}, 200


class GroupManagement(Resource):
    """Get and update Group models"""
    def get(self, id):
        """Get a group, return error if not found"""
        group = group_service.get_or_404(id)
        result = group_schema.dump(group)
        return {'success': True, 'group': result.data}, 200

    def delete(self, id):
        """Delete a group
        This will not effect Users (beyond removing their membership from the group)."""
        group = group_service.get_or_404(id)
        group_service.delete(group)
        return {'success': True}, 200

    @use_kwargs(group_update)
    def put(self, id, name, description):
        """Modify an existing group"""
        group = group_service.get_or_404(id)
        if description is missing:
            description=None
        group_service.update(group, name=name, description=description)
        result = group_schema.dump(group)
        return {'success': True, 'group': result.data}, 200


class GroupUsers(Resource):
    def get(self, id):
        """Return a list of the Group's users"""
        group = group_service.get_or_404(id)
        result = users_schema.dump(group.users)
        return {'success': True, 'users': result.data}, 200


class GroupUserCounts(Resource):
    def get(self):
        """Returns a list of Groups sorted by the number of users in
        (ascending) order along with a count of the users"""
        groups = group_service.all()
        groups.sort(key=lambda x: len(x.users))
        results = [{'name': group.name, 'id': group.id, 'user_count': len(group.users)}
                   for group in groups]
        return {'success': True, 'groups': results}, 200


api.add_resource(Groups, '')
api.add_resource(GroupUserCounts, '/user_counts')
api.add_resource(GroupManagement, '/<int:id>')
api.add_resource(GroupUsers, '/<int:id>/users')
