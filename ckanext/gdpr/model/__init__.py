import logging
from ckan import model
from ckan.model.meta import metadata, Session, mapper
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import types
from sqlalchemy import ForeignKey
from ckan.model.domain_object import DomainObject


log = logging.getLogger(__name__)

gdpr_accept_table = None
gdpr_policy_table = None
gdpr_table = None


def setup():
    if gdpr_table is None:
        define_gdpr_table()
        log.debug('GDPRTable table defined in memory')

    if model.resource_table.exists():
        if not gdpr_table.exists():
            gdpr_table.create()
            log.debug('GDPRTable table create')
        else:
            log.debug('GDPRTable table already exists')
    else:
        log.debug('GDPRTable table creation deferred')

    if gdpr_policy_table is None:
        define_gdpr_policy_table()
        log.debug('GDPRPolicyTable table defined in memory')

    if model.resource_table.exists():
        if not gdpr_policy_table.exists():
            gdpr_policy_table.create()
            log.debug('GDPRPolicyTable table create')
        else:
            log.debug('GDPRPolicyTable table already exists')
    else:
        log.debug('GDPRPolicyTable table creation deferred')

    if gdpr_accept_table is None:
        define_gdpr_accept_table()
        log.debug('GDPRAcceptTable table defined in memory')

    if model.resource_table.exists():
        if not gdpr_accept_table.exists():
            gdpr_accept_table.create()
            log.debug('GDPRAcceptTable table create')
        else:
            log.debug('GDPRAcceptTable table already exists')
    else:
        log.debug('GDPRAcceptTable table creation deferred')


class GDPRAccept(DomainObject):
    @classmethod
    def filter(cls, **kwargs):
        return Session.query(cls).filter_by(**kwargs)

    @classmethod
    def exists(cls, **kwargs):
        if cls.filter(**kwargs).first():
            return True
        else:
            return False

    @classmethod
    def get(cls, **kwargs):
        instance = cls.filter(**kwargs).first()
        return instance

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        Session.add(instance)
        Session.commit()
        return instance.as_dict()


def define_gdpr_accept_table():
    global gdpr_accept_table

    gdpr_accept_table = Table(
        'gdpr_accept', metadata,
        Column('id', types.Integer,
               primary_key=True,
               nullable=False,
               autoincrement=True),
        Column('user_id', types.UnicodeText,
               ForeignKey('user.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               nullable=False),
        Column('policy_id', types.Integer,
               ForeignKey('gdpr_policy.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               nullable=False)
    )

    mapper(
        GDPRAccept,
        gdpr_accept_table,
    )


class GDPRPolicy(DomainObject):
    @classmethod
    def filter(cls, **kwargs):
        return Session.query(cls).filter_by(**kwargs)

    @classmethod
    def exists(cls, **kwargs):
        if cls.filter(**kwargs).first():
            return True
        else:
            return False

    @classmethod
    def get(cls, **kwargs):
        instance = cls.filter(**kwargs).first()
        return instance

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        Session.add(instance)
        Session.commit()
        return instance.as_dict()

    @classmethod
    def delete(cls, **kwargs):
        instance = cls(**kwargs)
        Session.delete(instance)
        Session.flush()
        Session.commit()
        return None


def define_gdpr_policy_table():
    global gdpr_policy_table

    gdpr_policy_table = Table(
        'gdpr_policy', metadata,
        Column('id', types.Integer,
               primary_key=True,
               nullable=False,
               autoincrement=True),
        Column('content', types.UnicodeText,
               nullable=False),
        Column('required', types.Boolean,
               nullable=False),
        Column('gdpr_id', types.Integer,
               ForeignKey('gdpr.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               nullable=False),
    )

    mapper(
        GDPRPolicy,
        gdpr_policy_table,
    )


class GDPR(DomainObject):
    @classmethod
    def filter(cls, **kwargs):
        return Session.query(cls).filter_by(**kwargs)

    @classmethod
    def exists(cls, **kwargs):
        if cls.filter(**kwargs).first():
            return True
        else:
            return False

    @classmethod
    def get(cls, **kwargs):
        instance = cls.filter(**kwargs).first()
        return instance

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        Session.add(instance)
        Session.commit()
        return instance.as_dict()


def define_gdpr_table():
    global gdpr_table

    gdpr_table = Table(
        'gdpr', metadata,
        Column('id', types.Integer,
               primary_key=True,
               nullable=False,
               autoincrement=True),
        Column('tos', types.UnicodeText,
               nullable=False),
    )

    mapper(
        GDPR,
        gdpr_table,
    )
