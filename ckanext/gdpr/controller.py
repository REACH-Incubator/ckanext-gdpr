import logging

import ckan.plugins.toolkit as toolkit
from ckan.common import c, request
from ckan.controllers.user import UserController
from ckanext.gdpr import schema
from ckanext.gdpr.model import GDPR, GDPRPolicy

log = logging.getLogger(__name__)


class GDPRUserController(UserController):
    new_user_form = 'user/register.html'

    def _save_new(self, context):
        context['schema'] = schema.user_new_form_schema()
        return UserController._save_new(self, context)


class GDPRController(toolkit.BaseController):

    def gdpr(self):
        if request.method == 'GET':
            gdpr = GDPR.get()
            c.tos = ''
            c.policies = {}
            if gdpr is not None:
                c.tos = gdpr.tos
                c.policies = GDPRPolicy.filter(gdpr_id=gdpr.id)

            return toolkit.render('gdpr/gdpr.html')
