from functools import cached_property
from typing import Type

from inflection import underscore
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, declared_attr

from strawberry_mage.core.models import EntityModel

_Base = declarative_base()


class _BaseMeta(type(EntityModel), type(_Base)):
    pass


class _SQLAlchemyModel(EntityModel, _Base, metaclass=_BaseMeta):
    __abstract__ = True

    @declared_attr
    def __tablename__(self):
        return underscore(self.__name__)

    @cached_property
    def __primary_key__(self):
        return [c.name for c in inspect(self).primary_key]

    @cached_property
    def __primary_key_autogenerated__(self):
        return all(c.autoincrement for c in inspect(self).primary_key)


def create_base_entity(engine: Engine) -> Type[_SQLAlchemyModel]:
    from strawberry_mage.backends.sqlalchemy.backend import SQLAlchemyBackend

    new_base = declarative_base()
    return type(
        "SQLAlchemyModel",
        (
            new_base,
            _SQLAlchemyModel,
        ),
        {"__backend__": SQLAlchemyBackend(engine), "__abstract__": True},
    )
