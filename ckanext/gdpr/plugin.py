import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.logic.action.create import user_create
from ckanext.gdpr.model import setup as model_setup
from ckanext.gdpr.model import GDPR, GDPRPolicy, GDPRAccept
import ckan.model as model

log = logging.getLogger(__name__)


def gdpr_user_create(context, data_dict):
    user_dict = user_create(context, data_dict)
    for key, value in data_dict.items():
        if key.startswith('policy-'):
            policy_id = int(key.replace('policy-', ''))
            GDPRAccept.create(user_id=user_dict['id'], policy_id=policy_id)
    model.repo.commit()


def get_gdpr():
    return GDPR.get()


def get_policies(gdpr_id):
    return GDPRPolicy.filter(gdpr_id=gdpr_id).order_by(GDPRPolicy.id)


class GdprPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.ITemplateHelpers)

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
        map.connect('/gdpr',
                    controller='ckanext.gdpr.controller:GDPRController',
                    action='gdpr')

        return map

    # IActions

    def get_actions(self):
        return {'user_create': gdpr_user_create}

    # IConfigurable

    def configure(self, config):
        model_setup()

    # ITemplateHelpers

    def get_helpers(self):
        return {'get_gdpr': get_gdpr,
                'get_policies': get_policies}
