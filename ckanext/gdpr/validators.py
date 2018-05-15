import ckan.lib.navl.dictization_functions as df
from ckan.common import _
from ckanext.gdpr.model import GDPR, GDPRPolicy

Missing = df.Missing


def gdpr_accepted(key, data, errors, context):
    value = data[key]

    # policies = GDPRPolicy.filter(gdpr_id=gdpr.id).order_by(GDPRPolicy.id)

    if not value:
        # errors['terms_of_use'].append(
        #     _('You must accept required clauses of the terms of use'))
        errors[('terms_of_use',)] = [
            _('You must accept required clauses of the terms of use')]
