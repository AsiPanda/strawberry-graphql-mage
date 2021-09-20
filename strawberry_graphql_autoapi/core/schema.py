from typing import Dict

import strawberry
from inflection import underscore, pluralize
from strawberry import Schema

from strawberry_graphql_autoapi.core.type_creator import GeneratedType
from strawberry_graphql_autoapi.core.types import GraphQLOperation, IEntityModel, ISchemaManager


class SchemaManager(ISchemaManager):
    _models: Dict[str, IEntityModel]

    def __init__(self, *models):
        self._models = {m: GeneratedType.ENTITY.get_typename(m.__name__) for m in models}
        for model in self._models.values():
            model.setup(self)

    @staticmethod
    def _add_operation(type_object, operation: GraphQLOperation, model: IEntityModel):
        if operation in model.get_operations():
            name = model.__name__

            if operation.value % 2 == 0:
                name = pluralize(name)
            name = underscore(name)
            if operation.value > 2:
                name = operation.name.lower().split('_')[0] + '_' + name

            setattr(type_object, name, getattr(model.get_strawberry_type(), operation.name.lower()))
            return

    def get_models(self):
        return self._models[:]

    def get_model_for_name(self, name: str):
        return self._models.get(name, None)

    def get_schema(self):
        query_object = type('Query', (object,), {})
        mutation_object = type('Mutation', (object,), {})

        for model in self._models.values():
            # Query
            self._add_operation(query_object, GraphQLOperation.QUERY_ONE, model)
            self._add_operation(query_object, GraphQLOperation.QUERY_MANY, model)

            # Create
            self._add_operation(mutation_object, GraphQLOperation.CREATE_ONE, model)
            self._add_operation(mutation_object, GraphQLOperation.CREATE_MANY, model)

            # Update
            self._add_operation(mutation_object, GraphQLOperation.UPDATE_ONE, model)
            self._add_operation(mutation_object, GraphQLOperation.UPDATE_MANY, model)

            # Delete
            self._add_operation(mutation_object, GraphQLOperation.DELETE_ONE, model)
            self._add_operation(mutation_object, GraphQLOperation.DELETE_MANY, model)

        query = strawberry.type(query_object)
        mutation = strawberry.type(mutation_object)

        if len(mutation.__annotations__) > 0:
            return Schema(query=query, mutation=mutation)
        return Schema(query=query)
