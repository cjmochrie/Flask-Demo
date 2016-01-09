from datetime import date


from .core import db

# Association table enables many-to-many relation
groups_users = db.Table('groups_users',
                        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                        db.Column('group_id', db.Integer(), db.ForeignKey('group.id')))


class User(db.Model):
    """User Table"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    date_created = db.Column(db.Date(), nullable=False)
    groups = db.relationship('Group',
                             secondary=groups_users,
                             back_populates='users',
                             order_by='Group.name')

    @property
    def group_ids(self):
        return [group.id for group in self.groups]

    def __init__(self, *, name, email):
        self.name = name
        self.email = email
        self.date_created = date.today()

    def __repr__(self):
        return 'Name: {}, Email: {}, Date Created: {}'.\
            format(self.name, self.email, self.date_created)


class Group(db.Model):
    """Group table"""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True, index=True)
    description = db.Column(db.String(255))
    date_created = db.Column(db.Date(), nullable=False)
    users = db.relationship('User',
                            secondary=groups_users,
                            back_populates='groups',
                            order_by='User.name')

    def __init__(self, *, name, description):
        self.name = name
        self.description = description
        self.date_created = date.today()

    def __repr__(self):
        return 'Name: {}, Description: {}, Date Created: {}'.\
            format(self.name, self.description, self.date_created)

    @property
    def user_ids(self):
        return [user.id for user in self.users]

