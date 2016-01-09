from werkzeug.exceptions import Conflict, NotFound

class UserAlreadyExists(Conflict):
    pass

class UserNotFound(NotFound):
    pass

class GroupAlreadyExists(Conflict):
    pass

class GroupNotFound(NotFound):
    pass

# Errors dictionary for Flask Restful
errors = {
    'UserAlreadyExists': {
        'message': 'A user with that email already exists.',
        'status': 409,
        'success': False
    },
    'UserNotFound': {
        'message': 'User not found.',
        'status': 404,
        'success': False
    },
    'GroupAlreadyExists': {
        'message': 'A group with that name already exists.',
        'status': 409,
        'success': False
    },
    'GroupNotFound': {
        'message': 'Group not found.',
        'status': 404,
        'success': False
    }
}
