import datetime
import logging

import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.logic.action.create import user_create
from ckan.logic.action.update import user_update
from ckanext.gdpr import schema
from ckanext.gdpr.model import setup as model_setup
from ckanext.gdpr.model import GDPR, GDPRAccept, GDPRPolicy

log = logging.getLogger(__name__)


def gdpr_user_create(context, data_dict):
    user_dict = user_create(context, data_dict)
    for key, value in data_dict.items():
        if key.startswith('policy-'):
            policy_id = int(key.replace('policy-', ''))
            GDPRAccept.create(user_id=user_dict['id'], policy_id=policy_id,
                              datetime=datetime.datetime.now())
        model.repo.commit()
    return user_dict


def gdpr_user_update(context, data_dict):
    context['schema'] = schema.default_update_user_schema()
    user_dict = user_update(context, data_dict)
    gdpr_accept_list = GDPRAccept.filter(user_id=user_dict['id'])
    delete_list = []
    for gdpr_accept in gdpr_accept_list:
        if 'policy-{}'.format(gdpr_accept.policy_id) not in data_dict.keys():
            delete_list.append(gdpr_accept.id)

    for _id in delete_list:
        GDPRAccept.delete(id=_id)

    for key, value in data_dict.items():
        if key.startswith('policy-'):
            policy_id = int(key.replace('policy-', ''))
            if GDPRAccept.get(user_id=user_dict['id'],
                              policy_id=policy_id) is None:
                GDPRAccept.create(user_id=user_dict['id'], policy_id=policy_id,
                                  datetime=datetime.datetime.now())
                model.repo.commit()
    return user_dict


def get_gdpr():
    return GDPR.get()


def get_policies(gdpr_id):
    return GDPRPolicy.filter(gdpr_id=gdpr_id).order_by(GDPRPolicy.id)


def check_user_accepted_policy(user_id, policy_id):
    gdpr_accept = GDPRAccept.get(user_id=user_id, policy_id=policy_id)
    if gdpr_accept is not None:
        return True
    return False


def user_list(context, data_dict):
    return {'success': False}


class GdprPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'gdpr')

    # IRoutes

    def before_map(self, map):
        map.connect('/user/register',
                    controller='ckanext.gdpr.controller:GDPRUserController',
                    action='register')
        map.connect('/user/edit/me',
                    controller='ckanext.gdpr.controller:GDPRUserController',
                    action='edit_me')
        map.connect('/user/edit/{id}',
                    controller='ckanext.gdpr.controller:GDPRUserController',
                    action='edit')
        map.connect('/gdpr',
                    controller='ckanext.gdpr.controller:GDPRController',
                    action='gdpr')
        map.connect('/gdpr/policy',
                    controller='ckanext.gdpr.controller:GDPRController',
                    action='policies')
        map.connect('/gdpr/policy/{policy_id}',
                    controller='ckanext.gdpr.controller:GDPRController',
                    action='policy')
        map.connect('/gdpr/csv',
                    controller='ckanext.gdpr.controller:GDPRController',
                    action='policy_csv')

        return map

    # IActions

    def get_actions(self):
        return {'user_create': gdpr_user_create,
                'user_update': gdpr_user_update}

    # IConfigurable

    def configure(self, config):
        model_setup()

    # ITemplateHelpers

    def get_helpers(self):
        return {'get_gdpr': get_gdpr,
                'get_policies': get_policies,
                'check_user_accepted_policy': check_user_accepted_policy}

    # IAuthFunctions

    def get_auth_functions(self):
        return {'user_list': user_list}
