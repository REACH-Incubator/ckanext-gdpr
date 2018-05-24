import csv
import io
import logging

import ckan.authz as authz
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
from ckan.common import _, c, request, response
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

    def login(self, error=None):
        # Do any plugin login stuff
        for item in p.PluginImplementations(p.IAuthenticator):
            item.login()

        if 'error' in request.params:
            h.flash_error(request.params['error'])

        came_from = request.params.get('came_from')

        if not c.user:
            if not came_from:
                came_from = h.url_for(controller='user', action='logged_in')
            c.login_handler = h.url_for(
                self._get_repoze_handler('login_handler_path'),
                came_from=came_from)
            if error:
                vars = {'error_summary': {'': error}}
            else:
                vars = {}
            return toolkit.render('user/login.html', extra_vars=vars)
        elif came_from:
            return redirect(came_from)
        else:
            return toolkit.render('user/logout_first.html')


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
                gdpr = GDPR.get()
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

    def policy_csv(self):
        if not authz.is_sysadmin(c.user):
            abort(403, _('Unauthorized'))

        with io.BytesIO() as csvfile:
            fieldnames = ['user_id', 'username', 'email']

            gdpr = GDPR.get()
            policies = GDPRPolicy.filter(gdpr_id=gdpr.id)
            for policy in policies:
                fieldname = 'policy_id_{}'.format(policy.id)
                if policy.required:
                    fieldname += '*'
                fieldnames.append(fieldname)

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for user in User.all():
                csv_dict = {'user_id': user.id, 'username': user.name,
                            'email': user.email}

                policies = GDPRPolicy.filter(gdpr_id=gdpr.id)
                for policy in policies:
                    user_accept = GDPRAccept.get(policy_id=policy.id,
                                                 user_id=user.id)
                    accepted = False
                    if user_accept is not None:
                        accepted = True

                    fieldname = 'policy_id_{}'.format(policy.id)
                    if policy.required:
                        fieldname += '*'
                    csv_dict[fieldname] = accepted

                writer.writerow(csv_dict)

            response.headers['Content-type'] = 'text/csv'
            return csvfile.getvalue()
