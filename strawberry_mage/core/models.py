from typing import Any, Set, List, Type, Dict, Tuple, Optional

from strawberry.types import Info

from strawberry_mage.core.resolver import resolver_query_one, resolver_query_many, resolver_create_one, \
    resolver_create_many, resolver_update_one, resolver_update_many, resolver_delete_one, resolver_delete_many
from strawberry_mage.core.strawberry_types import StrawberryModelType
from strawberry_mage.core.type_creator import create_entity_type, \
    create_input_types, create_filter_input, create_ordering_input
from strawberry_mage.core.types import GraphQLOperation, IEntityModel, IDataBackend, ISchemaManager


class EntityModel(IEntityModel):

    __backend__: IDataBackend = None
    __primary_key__: Any = None
    _strawberry_type: StrawberryModelType
    _properties: List[str]
    _manager: ISchemaManager = None

    def __hash__(self):
        return hash(f'{self.__name__}({",".join(getattr(self, a) for a in self.get_primary_key())})')

    @classmethod
    def get_strawberry_type(cls):
        return cls._strawberry_type

    @classmethod
    def get_primary_key(cls) -> Tuple:
        return cls.__backend__.get_primary_key(cls)

    @classmethod
    def resolve(cls, operation: GraphQLOperation, info: Info, data: Any):
        return cls.__backend__.resolve(cls, operation, info, data)

    @classmethod
    def get_operations(cls) -> Set[GraphQLOperation]:
        return cls.__backend__.get_operations(cls)

    @classmethod
    def get_attributes(cls, operation: Optional[GraphQLOperation] = None) -> List[str]:
        return cls.__backend__.get_attributes(cls, operation)

    @classmethod
    def get_attribute_types(cls) -> Dict[str, Type]:
        return cls.__backend__.get_attribute_types(cls)

    @classmethod
    def get_attribute_type(cls, attr: str) -> Type:
        return cls.__backend__.get_attribute_type(cls, attr)

    @classmethod
    def get_schema_manager(cls) -> ISchemaManager:
        return cls._manager

    @classmethod
    def get_parent_class_name(cls) -> Optional[str]:
        return cls.__backend__.get_parent_class_name(cls)

    @classmethod
    def get_children_class_names(cls) -> Optional[List[str]]:
        return cls.__backend__.get_children_class_names(cls)

    @classmethod
    def pre_setup(cls, manager):
        cls._manager = manager
        cls._properties = cls.__backend__.get_attributes(cls)
        base_entity, entity = create_entity_type(cls)
        cls._strawberry_type = StrawberryModelType(
            base_entity=base_entity,
            entity=entity,
            filter=create_filter_input(cls),
            ordering=create_ordering_input(cls),
        )
        cls._strawberry_type.input_types = create_input_types(cls)
        cls._strawberry_type.query_one = resolver_query_one(cls)
        cls._strawberry_type.query_many = resolver_query_many(cls)
        cls._strawberry_type.create_one = resolver_create_one(cls)
        cls._strawberry_type.create_many = resolver_create_many(cls)
        cls._strawberry_type.update_one = resolver_update_one(cls)
        cls._strawberry_type.update_many = resolver_update_many(cls)
        cls._strawberry_type.delete_one = resolver_delete_one(cls)
        cls._strawberry_type.delete_many = resolver_delete_many(cls)
        return cls

    @classmethod
    def post_setup(cls) -> None:
        pass
