from orator import DatabaseManager
from douyin.core import settings
from orator import Model

db = DatabaseManager(settings.DATABASES)
Model.set_connection_resolver(db)

class AdminImport(Model):
    __table__ = 'dy_admin_imports'
    __primary_key__ = 'id'
    __unguarded__ = True

class DyUser(Model):
    __table__ = 'dy_users'
    __primary_key__ = 'id'
    __unguarded__ = True

class DyTag(Model):
    __table__ = 'dy_tags'
    __primary_key__ = 'id'
    __unguarded__ = True

class Keyword(Model):
    __table__ = 'keywords'
    __primary_key__ = 'id'
    __unguarded__ = True