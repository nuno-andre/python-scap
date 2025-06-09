import warnings

from pydantic import (
    BaseModel, Field, ConfigDict,
    field_validator, model_validator, computed_field,
)
from pydantic.alias_generators import to_camel


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
        validate_by_name = True,
        use_enum_values  = True,
        extra            = 'ignore',
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


warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message=r'Field name .* shadows an attribute in parent .*',
)
