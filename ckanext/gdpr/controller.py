import logging

import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.common import c, request
from ckan.controllers.user import UserController
from ckanext.gdpr import schema
from ckanext.gdpr.model import GDPR, GDPRPolicy
from pylons.controllers.util import redirect

log = logging.getLogger(__name__)


class GDPRUserController(UserController):
    new_user_form = 'user/register.html'

    def _save_new(self, context):
        context['schema'] = schema.user_new_form_schema()
        return UserController._save_new(self, context)


class GDPRController(toolkit.BaseController):

    def gdpr(self):
        gdpr = GDPR.get()
        if request.method == 'GET':
            c.tos = ''
            c.policies = {}
            if gdpr is not None:
                c.tos = gdpr.tos
                c.policies = GDPRPolicy.filter(gdpr_id=gdpr.id)

            return toolkit.render('gdpr/gdpr.html')

        if request.method == 'POST':
            log.debug(request.POST)
            if gdpr is None:
                GDPR.create(
                    tos=request.POST.get('tos')
                )
                gdpr = GDPR.get()

            # Create new policies
            for key in request.POST.iterkeys():
                if key.startswith('policy-'):
                    required = False
                    if 'required-{}'.format(key) in request.POST:
                        required = True
                    GDPRPolicy.create(
                        content=request.POST.get(key),
                        required=required,
                        gdpr_id=gdpr.id
                    )

            model.repo.commit()

            return redirect('/gdpr')
