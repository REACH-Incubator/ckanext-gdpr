import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.logic.create import user_create
from ckanext.gdpr.model import setup as model_setup


def gdpr_user_create(context, data_dict):
    user_dict = user_create(context, data_dict)


class GdprPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IConfigurable, inherit=True)

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

        return map

    # IActions

    def get_actions(self):
        return {'user_create': gdpr_user_create}

    # IConfigurable

    def configure(self, config):
        model_setup()
