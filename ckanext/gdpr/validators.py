import ckan.lib.navl.dictization_functions as df
from ckan.common import _

Missing = df.Missing
Invalid = df.Invalid


def gdpr_accepted(key, data, errors, context):
    value = data[key]

    if not value:
        errors[('terms_of_use',)] = [
            _('You must accept required clauses of the terms of use')]


def not_me(key, data, errors, context):
    value = data[key]

    if value.lower() == 'me':
        raise Invalid(_('That name cannot be used'))
