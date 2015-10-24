# -*- coding: utf-8 -*-
import logging
import tg
from tgext.pluggable import PluggableSession

log = logging.getLogger('tgapp-tgappgooglePlusAuth')

DBSession = PluggableSession()
GoogleAuth = None


def init_model(app_session):
    DBSession.configure(app_session)


def import_models():
    global GoogleAuth
    if tg.config.get('use_sqlalchemy', False):
        from .sqla_models import GoogleAuth
    elif tg.config.get('use_ming', False):
        from .ming_models import GoogleAuth


class PluggableSproxProvider(object):
    def __init__(self):
        self._provider = None

    def _configure_provider(self):
        if tg.config.get('use_sqlalchemy', False):
            log.info('Configuring googlePlusAuth for SQLAlchemy')
            from sprox.sa.provider import SAORMProvider
            self._provider = SAORMProvider(session=DBSession)
        elif tg.config.get('use_ming', False):
            log.info('Configuring googlePlusAuth for Ming')
            from sprox.mg.provider import MingProvider
            self._provider = MingProvider(DBSession)
        else:
            raise ValueError('googlePlusAuth should be used with sqlalchemy or ming')

    def __getattr__(self, item):
        if self._provider is None:
            self._configure_provider()

        if hasattr(self, item):
            # _configure_provider might add additional attributes
            return getattr(self, item)

        return getattr(self._provider, item)

    def add_user(self, u):
        if self._provider is None:
            self._configure_provider()
        if tg.config.get('use_sqlalchemy', False):
            self._provider.session.add(u)
        elif tg.config.get('use_ming', False):
            self._provider.session.flush_all()
        else:
            raise ValueError('googlePlusAuth should be used with sqlalchemy or ming')

provider = PluggableSproxProvider()
