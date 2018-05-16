from ckan.lib.navl.validators import ignore, ignore_missing, not_empty
from ckan.logic.validators import (ignore_not_sysadmin, name_validator,
                                   user_about_validator,
                                   user_both_passwords_entered,
                                   user_name_validator,
                                   user_password_not_empty,
                                   user_password_validator,
                                   user_passwords_match)
from ckanext.gdpr.model import GDPR, GDPRPolicy
from ckanext.gdpr.validators import gdpr_accepted, not_me


def default_user_schema():
    schema = {
        'id': [ignore_missing, unicode],
        'name': [not_empty, name_validator, user_name_validator, not_me,
                 unicode],
        'fullname': [ignore_missing, unicode],
        'password': [user_password_validator, user_password_not_empty,
                     ignore_missing, unicode],
        'password_hash': [ignore_missing, ignore_not_sysadmin, unicode],
        'email': [not_empty, unicode],
        'about': [ignore_missing, user_about_validator, unicode],
        'created': [ignore],
        'openid': [ignore_missing],
        'sysadmin': [ignore_missing, ignore_not_sysadmin],
        'apikey': [ignore],
        'reset_key': [ignore],
        'activity_streams_email_notifications': [ignore_missing],
        'state': [ignore_missing],
    }
    gdpr = GDPR.get()
    policies = GDPRPolicy.filter(gdpr_id=gdpr.id)
    for policy in policies:
        if policy.required:
            schema['policy-{}'.format(policy.id)] = [gdpr_accepted]
    return schema


def user_new_form_schema():
    schema = default_user_schema()

    schema['password1'] = [unicode, user_both_passwords_entered,
                           user_password_validator, user_passwords_match]
    schema['password2'] = [unicode]

    return schema


def default_update_user_schema():
    schema = default_user_schema()

    schema['name'] = [ignore_missing, name_validator, user_name_validator,
                      unicode]
    schema['password'] = [user_password_validator, ignore_missing, unicode]

    return schema
