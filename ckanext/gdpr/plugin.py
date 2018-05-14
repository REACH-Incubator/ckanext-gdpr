import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class GdprPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

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