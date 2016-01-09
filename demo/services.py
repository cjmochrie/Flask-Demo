from .core import Service
from .errors import UserAlreadyExists, UserNotFound
from .errors import GroupAlreadyExists, GroupNotFound
from .models import User, Group

# Instantiate services and assign custom errors
user_service = Service(User,
                       error_conflict=UserAlreadyExists,
                       error_404=UserNotFound)

group_service =Service(Group,
                       error_conflict=GroupAlreadyExists,
                       error_404=GroupNotFound)
