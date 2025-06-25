from typing import Annotated, Any
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import backref, relationship

from scap._core.sql import BaseSqlModel, Field, Relationship
from scap._core.schema import field_validator
from scap._core._types import AnyUrl
from scap.schemas.cpe import CpeName


class SqlCpeDeprecation(BaseSqlModel, table=True):
    deprecated_by_id: UUID = Field(primary_key=True, foreign_key='cpe_item.id')
    deprecates_id:    UUID = Field(primary_key=True, foreign_key='cpe_item.id')


class SqlCpeReference(BaseSqlModel, table=True):
    id:     int | None = Field(default=None, primary_key=True)
    ref:    Annotated[str, AnyUrl] = Field(max_length=2048)
    type:   str | None = Field(None, max_length=10, nullable=True)
    cpe_id: UUID = Field(None, foreign_key='cpe_item.id', nullable=True)


class SqlCpeItem(BaseSqlModel, table=True):
    id:            UUID = Field(primary_key=True)
    name:          CpeName = Field(unique=True, sa_column_kwargs={'index': True})
    part:          str
    vendor:        str
    product:       str
    version:       str
    deprecated:    bool
    created:       datetime
    last_modified: datetime
    title:         str

    refs:          list[SqlCpeReference] = Relationship(
        sa_relationship_kwargs={
            'lazy': 'selectin',
            'backref': backref('cpe_ref', lazy='selectin'),
        },
    )

    @field_validator('created', 'last_modified', mode='before')
    @classmethod
    def ensure_utc(cls, v: Any) -> datetime:
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


SqlCpeItem.deprecated_by = relationship(
    'SqlCpeItem',
    secondary=SqlCpeDeprecation.__table__,
    primaryjoin=SqlCpeItem.id == SqlCpeDeprecation.deprecates_id,
    secondaryjoin=SqlCpeItem.id == SqlCpeDeprecation.deprecated_by_id,
    lazy='selectin',
    back_populates='deprecates',
)


SqlCpeItem.deprecates = relationship(
    'SqlCpeItem',
    secondary=SqlCpeDeprecation.__table__,
    primaryjoin=SqlCpeItem.id == SqlCpeDeprecation.deprecated_by_id,
    secondaryjoin=SqlCpeItem.id == SqlCpeDeprecation.deprecates_id,
    lazy='selectin',
    back_populates='deprecated_by',
)
