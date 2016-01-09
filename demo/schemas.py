from marshmallow import Schema, fields

class UserSchema(Schema):
    """Schema for User model serialization"""
    id = fields.Integer(dump_only=True)
    name = fields.Str()
    email = fields.Str()
    date_created = fields.Date()
    group_ids = fields.List(fields.Integer())


class GroupSchema(Schema):
    """Schema for Group model serialization"""
    id = fields.Integer(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    date_created = fields.Date()
    user_ids = fields.List(fields.Integer())

# Instantiate schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)