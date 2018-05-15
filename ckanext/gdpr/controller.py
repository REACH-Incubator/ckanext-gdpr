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
                c.policies = GDPRPolicy.filter(gdpr_id=gdpr.id).order_by(
                    GDPRPolicy.id)

            return toolkit.render('gdpr/gdpr.html')

        if request.method == 'POST':
            log.debug(request.POST)
            if gdpr is None:
                GDPR.create(
                    tos=request.POST.get('tos')
                )
            else:
                gdpr.tos = request.POST.get('tos')

            # Create new policies
            log.debug('Creating new policies')
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

            # Update existing policies
            for key in request.POST.iterkeys():
                if not key.startswith(('policy-', 'required-', 'tos')):
                    required = False
                    if 'required-{}'.format(key) in request.POST:
                        required = True
                    policy = GDPRPolicy.get(id=key)
                    policy.content = request.POST.get(key)
                    policy.required = required
                    policy.save()
                    model.repo.commit()

            model.repo.commit()

            return redirect('/gdpr')
