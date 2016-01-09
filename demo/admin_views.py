from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView


# Create customized model view class
class DbView(ModelView):
    column_display_pk = True
    column_auto_select_related = True
    edit_modal = True
    column_default_sort = ('id', True)
    page_size = 40
    can_create = False


class AdminView(BaseView):
    def is_accessible(self):

        return True
