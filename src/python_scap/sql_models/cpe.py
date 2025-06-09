from typing import Annotated
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import backref, relationship

from python_scap._core.sql import BaseSqlModel, Field, Relationship
from python_scap._core._types import AnyUrl
from python_scap.schemas.cpe import CpeName


class Deprecation(BaseSqlModel, table=True):
    deprecated_by_id: UUID = Field(primary_key=True, foreign_key='cpe_item.id')
    deprecates_id:    UUID = Field(primary_key=True, foreign_key='cpe_item.id')


class SqlCpeReference(BaseSqlModel, table=True):
    ref:    Annotated[str, AnyUrl] = Field(primary_key=True)
    type:   str | None = Field(None, primary_key=True, nullable=True)
    cpe_id: UUID = Field(None, primary_key=True, foreign_key='cpe_item.id', nullable=True)


class SqlCpeItem(BaseSqlModel, table=True):
    id:            UUID = Field(primary_key=True)
    name:          CpeName = Field(unique=True, sa_column_kwargs={'index': True})
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


SqlCpeItem.deprecated_by = relationship(
    'SqlCpeItem',
    secondary=Deprecation.__table__,
    primaryjoin=SqlCpeItem.id == Deprecation.deprecates_id,
    secondaryjoin=SqlCpeItem.id == Deprecation.deprecated_by_id,
    lazy='selectin',
    back_populates='deprecates',
)


SqlCpeItem.deprecates = relationship(
    'SqlCpeItem',
    secondary=Deprecation.__table__,
    primaryjoin=SqlCpeItem.id == Deprecation.deprecated_by_id,
    secondaryjoin=SqlCpeItem.id == Deprecation.deprecates_id,
    lazy='selectin',
    back_populates='deprecated_by',
)
