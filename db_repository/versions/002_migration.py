from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
cuota = Table('cuota', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('valor', Float),
    Column('fecha', Date),
    Column('fondo', String(length=1)),
    Column('AFP_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cuota'].columns['AFP_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cuota'].columns['AFP_id'].drop()
