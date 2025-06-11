from typing import Pattern
from enum import Enum

from pydantic import AnyUrl, GetCoreSchemaHandler
from pydantic_core import core_schema


__all__ = ['StrEnum', 'AnyUrl', 'RegexString']


class StrEnum(str, Enum):
    __str__ = str.__str__


class RegexStringMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs):

        if name != 'RegexString':

            if (pattern := namespace.get('__pattern__', None)) is None:
                for base in bases:
                    if (pattern := getattr(base, '__pattern__', None)):
                        break
                else:
                    raise TypeError(f"{name!r} must define a '__pattern__' attribute")

            if not isinstance(pattern, Pattern):
                raise TypeError(f'{name}.__pattern__ must be a compiled regex pattern')

            namespace['__slots__'] = list(pattern.groupindex.keys())

        return super().__new__(cls, name, bases, namespace)


class RegexString(str, metaclass=RegexStringMeta):

    __slots__ = ['__pattern__']
    __pattern__: Pattern[str]

    def __new__(cls, value: str):
        if not (match := cls.__pattern__.fullmatch(value)):
            raise TypeError(f'Invalid {cls.__name__!r}')

        for k,v in match.groupdict().items():
            setattr(cls, k, v)

        return super().__new__(cls, value)

    def __contains__(self, item: str) -> bool:
        return any(item == getattr(self, slot) for slot in self.__slots__)

    def __repr__(self) -> str:
        attrs = ', '.join(f'{slot}={getattr(self, slot)!r}' for slot in self.__slots__)
        return f'{self.__class__.__name__}({attrs})'

    @classmethod
    def __get_pydantic_core_schema__(cls, _source, _handler: GetCoreSchemaHandler):
        pattern = ''.join(map(str.strip, cls.__pattern__.pattern.splitlines()))
        return core_schema.str_schema(pattern=pattern)
