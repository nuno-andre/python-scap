from typing import Annotated
from datetime import datetime
from uuid import UUID
import re

from annotated_types import MinLen

from python_scap._core.schema import (
    BaseSchema, CamelBaseSchema, Field, computed_field,
)
from python_scap._core._types import StrEnum, AnyUrl, RegexString


_RE_ALNUM   = r'[A-Za-z0-9\-\._]'
_RE_ESC     = r'(?:\\[\\\*\?!"#\$%&\'\(\)\+,/:;<=>@\[\]\^`\{\|}~])'
_RE_ATOM    = rf'(?:\?*|\*?)(?:{_RE_ALNUM}|{_RE_ESC})+(?:\?*|\*?)'
_RE_COMPLEX = rf'(?:{_RE_ATOM}|[\*\-])'

# for `langugage` prop, but some CPEs don't follow RFC 5646  ¯\_(ツ)_/¯
# _RE_LANG = r'(?:[A-Za-z]{2,3}(?:-[A-Za-z]{2}|-[0-9]{3})?|[\*\-])'


class CpeName(RegexString):
    '''CPE Name URI.

    Example: `cpe:2.3:a:vendor:product:version:update:edition:language:sw_edition:target_sw:target_hw:other`
    '''  # noqa: E501

    __pattern__ = re.compile(rf'''
        cpe:2\.3:
        (?P<part>[aho\*\-]):
        (?P<vendor>{_RE_COMPLEX}):
        (?P<product>{_RE_COMPLEX}):
        (?P<version>{_RE_COMPLEX}):
        (?P<update>{_RE_COMPLEX}):
        (?P<edition>{_RE_COMPLEX}):
        (?P<language>{_RE_COMPLEX}):
        (?P<sw_edition>{_RE_COMPLEX}):
        (?P<target_sw>{_RE_COMPLEX}):
        (?P<target_hw>{_RE_COMPLEX}):
        (?P<other>{_RE_COMPLEX})
    ''', re.VERBOSE)


class ReferenceType(StrEnum):
    '''Internet resource for CPE.
    '''
    ADVISORY   = 'Advisory'
    CHANGE_LOG = 'Change Log'
    PRODUCT    = 'Product'
    PROJECT    = 'Project'
    VENDOR     = 'Vendor'
    VERSION    = 'Version'


class CpeReference(BaseSchema):
    ref:  Annotated[str, AnyUrl]
    type: ReferenceType | None = None


class CpeTitle(BaseSchema):
    '''Title of the CPE item.
    '''
    title: str
    lang:  str


class BaseCpe(CamelBaseSchema):
    '''Base class for CPE items.

    Attributes:
        name: CPE Name string.
        id:   UUID of the CPE Name.
    '''
    name: CpeName = Field(alias='cpeName')
    id:   UUID    = Field(alias='cpeNameId')


class CpeItem(BaseCpe):
    '''The CpeItem element denotes a single CPE Name.

    Attributes:
        titles: Titles of the CPE item.
        deprecated: Whether the item is deprecated.
    '''
    deprecated:    bool
    created:       datetime
    last_modified: datetime
    titles:        Annotated[list[CpeTitle], MinLen(1)]
    refs:          list[CpeReference] | None = None
    deprecated_by: list[BaseCpe] | None = None
    deprecates:    list[BaseCpe] | None = None

    @computed_field
    @property
    def title(self) -> str:
        return [t.title for t in self.titles if t.lang == 'en'][0]
