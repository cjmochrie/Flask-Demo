# Following the lead of @mattupstate here and with factory.py
# https://github.com/mattupstate/overholt/blob/master/overholt/core.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, NotFound

db = SQLAlchemy()

class Service:
    """Service for abstracting models and SQLAlchemy from the view layer"""
    def __init__(self, Model, error_conflict=None, error_404=None):
        """Initialize the service assigning the model class and custom Exceptions"""
        self.__model = Model
        self.error_conflict = error_conflict or Conflict
        self.error_404 = error_404 or NotFound

    def _is_instance(self, model):
        """Verify model is an instance of the Service's model class"""
        if not isinstance(model, self.__model):
            raise ValueError('{} is not an instance of {}'.
                             format(model, self.__model.__name__))

    def get(self, id):
        """Return a model instance by id"""
        return self.__model.query.get(id)

    def get_or_404(self, id):
        """Return a model instance by id.
        Raise custom Not Found error if it does not exist"""
        instance = self.get(id)
        if not instance:
            raise self.error_404
        return instance

    def all(self, *args):
        """Get all models, ordered by *args"""
        query = self.__model.query
        for arg in args:
            query = query.order_by(arg)
        return query.all()

    def delete(self, instance):
        """Delete an instance"""
        self._is_instance(instance)
        db.session.delete(instance)
        db.session.commit()

    def update(self, instance, **kwargs):
        """Update the instance and return"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.save(instance)
        return instance

    def save(self, instance):
        """Commit the instance. Raises custom Conflict error if an
        Integrity Error is caught"""
        self._is_instance(instance)
        db.session.add(instance)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise self.error_conflict

    def new(self, **kwargs):
        """Create a new model and return"""
        instance = self.__model(**kwargs)
        self.save(instance)
        return instance
