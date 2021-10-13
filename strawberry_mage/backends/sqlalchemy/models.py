from functools import cached_property

from inflection import underscore
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, as_declarative, declared_attr

from strawberry_mage.core.models import EntityModel
from strawberry_mage.core.types import IEntityModel


@as_declarative()
class _Base:
    @declared_attr
    def __tablename__(self):
        return underscore(self.__name__)


class _BaseMeta(type(IEntityModel), type(_Base)):
    pass


class _SQLAlchemyModel(_Base, EntityModel, metaclass=_BaseMeta):
    __abstract__ = True

    @cached_property
    def __primary_key__(self):
        return [c.name for c in inspect(self).primary_key]


def create_base_entity(engine: Engine):
    from strawberry_mage.backends.sqlalchemy.backend import SQLAlchemyBackend
    return type('SQLAlchemyModel', (_SQLAlchemyModel,), {
        '__backend__': SQLAlchemyBackend(engine),
        '__abstract__': True
    })
