from ckan.controllers.user import UserController
from ckanext.gdpr import schema


class GDPRUserController(UserController):
    new_user_form = 'user/register.html'

    def _save_new(self, context):
        context['schema'] = schema.user_new_form_schema()
        return UserController._save_new(self, context)
