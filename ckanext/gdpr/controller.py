import logging

import ckan.authz as authz
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.common import _, c, request
from ckan.controllers.user import UserController
from ckan.model.user import User
from ckanext.gdpr import schema
from ckanext.gdpr.model import GDPR, GDPRAccept, GDPRPolicy
from pylons.controllers.util import redirect

log = logging.getLogger(__name__)

abort = base.abort


class GDPRUserController(UserController):
    new_user_form = 'user/register.html'
    edit_user_form = 'user/gdpr_edit_user_form.html'

    def _save_new(self, context):
        context['schema'] = schema.user_new_form_schema()
        return UserController._save_new(self, context)

    def edit_me(self, locale=None):
        if not c.user:
            h.redirect_to(locale=locale, controller='user', action='login',
                          id=None)
        user_ref = c.userobj.get_reference_preferred_for_uri()
        h.redirect_to(locale=locale,
                      controller='ckanext.gdpr.controller:GDPRUserController',
                      action='edit',
                      id=user_ref)


class GDPRController(toolkit.BaseController):

    def gdpr(self):
        if not authz.is_sysadmin(c.user):
            abort(403, _('Unauthorized'))

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
                gdpr = GDPR.create(
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

    def policies(self):
        if not authz.is_sysadmin(c.user):
            abort(403, _('Unauthorized'))
        gdpr = GDPR.get()
        c.policies = GDPRPolicy.filter(gdpr_id=gdpr.id).order_by(GDPRPolicy.id)

        return toolkit.render('gdpr/policies.html')

    def policy(self, policy_id):
        if not authz.is_sysadmin(c.user):
            abort(403, _('Unauthorized'))
        c.policy = GDPRPolicy.get(id=policy_id)
        accepted_policy = GDPRAccept.filter(policy_id=c.policy.id)
        c.accepting_users = []
        for policy in accepted_policy:
            c.accepting_users.append(User.get(policy.user_id))

        c.not_accepting_users = [
            item for item in User.all() if item not in c.accepting_users]

        return toolkit.render('gdpr/policy.html')
