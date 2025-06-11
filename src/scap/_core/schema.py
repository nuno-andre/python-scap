from typing import TYPE_CHECKING
import warnings

from pydantic import (
    BaseModel, Field, ConfigDict,
    field_validator, model_validator, computed_field,
)
from pydantic.alias_generators import to_camel
from pydantic.json_schema import PydanticJsonSchemaWarning

if TYPE_CHECKING:
    from pydantic_core import CoreSchema
    from pydantic.annotated_handlers import GetJsonSchemaHandler
    from pydantic.json_schema import JsonSchemaValue


__all__ = [
    'BaseSchema',
    'Field',
    'CamelBaseSchema',
    'field_validator',
    'model_validator',
    'computed_field',
]


class BaseSchema(BaseModel):

    model_config = ConfigDict(
        validate_by_name        = True,
        use_enum_values         = True,
        extra                   = 'ignore',
    )

    def model_dump(self, **kwargs) -> dict:
        kwargs.setdefault('warnings', False)
        return super().model_dump(**kwargs)


class CamelBaseSchema(BaseSchema):
    '''Base schema for models that use camelCase for field names.
    '''

    model_config = ConfigDict(
        alias_generator = to_camel,
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: 'CoreSchema',
        handler:     'GetJsonSchemaHandler',
    ) -> 'JsonSchemaValue':
        # XXX: FastAPI hard encodes `by_alias=True` for docs
        # ^ https://github.com/fastapi/fastapi/discussions/9150
        for field in core_schema['schema']['fields']:
            core_schema['schema']['fields'][field]['serialization_alias'] = field
        return handler(core_schema)


warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message=r'Field name .* shadows an attribute in parent .*',
)

warnings.filterwarnings(
    'ignore',
    category=PydanticJsonSchemaWarning,
    message=r'.* \[non-serializable-default\]',
)
