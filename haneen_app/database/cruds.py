from contextlib import nullcontext
from datetime import datetime
from typing import Any, Dict, Iterable, List, Sequence, Type, TypeVar, Union, overload

from sqlalchemy import delete, insert, inspect, select, update
from sqlalchemy.engine import CursorResult, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapper
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import Delete, Insert, Select, Update
from haneen_app.database.data_store import Base
from haneen_app.utilities.conversions import to_dict


CudType = TypeVar("CudType", bound=Union[Select, Update, Delete])

BasicType = Union[str, int, float, bool, datetime]
EntityType = TypeVar("EntityType", bound=Base)
SelectEntityType = Union[Type[EntityType], InstrumentedAttribute]
SelectType = Union[SelectEntityType, List[SelectEntityType]]

CriteriaValueUnit = Union[BasicType, InstrumentedAttribute]
CriteriaValue = Union[CriteriaValueUnit, Sequence[CriteriaValueUnit]]
CriteriaKey = Union[str, InstrumentedAttribute]
Criteria = Dict[CriteriaKey, CriteriaValue]
StrCriteria = Dict[str, CriteriaValue]


def begin_transaction(session: AsyncSession):
    # When there is already a transaction going on, we don't need to begin a new transaction
    return nullcontext(session) if session.in_transaction() else session.begin()


@overload
async def get_by(
    session: AsyncSession,
    entity: Type[EntityType],
    criteria: Criteria = None,
    clauses: List = None,
    /,
) -> List[EntityType]:
    ...


@overload
async def get_by(
    session: AsyncSession,
    entities: List[SelectEntityType],
    criteria: Criteria = None,
    clauses: list = None,
    /,
) -> List[Row]:
    ...


@overload
async def get_by(
    session: AsyncSession,
    entity: InstrumentedAttribute,
    criteria: Criteria = None,
    clauses: List = None,
    /,
) -> List[BasicType]:
    ...


async def get_by(
    session: AsyncSession,
    entities: SelectType,
    criteria: Criteria = None,
    clauses: list = None,
    /,
) -> list:
    return await _get_by(session, entities, fetch_first=False, criteria=criteria, clauses=clauses)


@overload
async def get_first_by(
    session: AsyncSession,
    entity: Type[EntityType],
    criteria: Criteria = None,
    clauses: List = None,
    /,
) -> EntityType:
    ...


@overload
async def get_first_by(
    session: AsyncSession,
    columns: List[SelectEntityType],
    criteria: Criteria = None,
    clauses: List = None,
    /,
) -> Row:
    ...


@overload
async def get_first_by(
    session: AsyncSession,
    entity: InstrumentedAttribute,
    criteria: Criteria = None,
    clauses: list = None,
    /,
) -> BasicType:
    ...


async def get_first_by(
    session: AsyncSession,
    entities: SelectType,
    criteria: Criteria = None,
    clauses: list = None,
    /,
):
    return await _get_by(session, entities, fetch_first=True, criteria=criteria, clauses=clauses)


async def update_by(
    session: AsyncSession,
    entity: Type[Base],
    values: Dict[CriteriaKey, Any],
    criteria: Criteria = None,
    clauses: list = None,
):
    entity_type = entity
    table: Mapper = inspect(entity_type)

    if not criteria and not clauses:
        return

    async with begin_transaction(session):
        statement: Update = update(entity).returning(*table.primary_key)
        statement = statement.values(values)
        statement = build_where_statement(entity, statement, criteria, clauses)
        result: CursorResult = await session.execute(statement)
        results = result.fetchall()
    return results


async def delete_by(session: AsyncSession, entity: Type[Base], criteria: Criteria = None, clauses: list = None):
    if not criteria and not clauses:
        return

    async with begin_transaction(session):
        statement: Delete = delete(entity)
        statement = build_where_statement(entity, statement, criteria, clauses)
        await session.execute(statement)


async def delete_by_primary_key(session: AsyncSession, entity: Type[Base], keys: list):
    table: Mapper = inspect(entity)
    await delete_by(session, entity, {table.primary_key[0]: keys})


async def delete_all(session: AsyncSession, entity: Type[Base]):
    async with begin_transaction(session):
        statement: Delete = delete(entity)
        await session.execute(statement)


async def insert_with(
    session: AsyncSession, entities: List[EntityType], disable_constraint=False, disable_trigger=False
):
    entity_type = Type(entities[0])
    table: Mapper = inspect(entity_type)
    table_name: str = table.persist_selectable.fullname

    results = []
    async with begin_transaction(session):
        if disable_constraint:
            await session.execute(f"ALTER TABLE {table_name} NOCHECK CONSTRAINT ALL ")

        if disable_trigger:
            await session.execute(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL ")

        for entity in entities:
            statement: Insert = insert(entity_type).returning(*table.primary_key)
            statement = statement.values({table.c[k]: v for k, v in to_dict(entity).items()})
            result: CursorResult = await session.execute(statement)
            results.append(result.fetchall()[0][0])

    return results


async def cud(
    session: AsyncSession,
    inserts: Iterable[Base] = None,
    updates: Iterable[Base] = None,
    deletes: Iterable[Base] = None,
):
    async with begin_transaction(session):
        if inserts:
            session.add_all(inserts)

        if updates:
            session.add_all(updates)

        if deletes:
            session.add_all(deletes)  # Since these are detached entities, need to re-attach them first
            for entity in deletes:
                await session.delete(entity)

    if not session.in_transaction():
        # We don't want the inserted entities to be bound to session but only expunge when no transaction going on
        for entity in inserts or []:
            session.expunge(entity)

        for entity in updates or []:
            session.expunge(entity)


def build_where_statement(
    entity: Type[Base], statement: CudType, criteria: Criteria = None, clauses: list = None
) -> CudType:
    where_clauses = _build_clauses(entity, criteria, clauses)

    for clause in where_clauses:
        statement = statement.where(clause)

    return statement.execution_options(synchronize_session=False)


async def _get_by(
    session: AsyncSession,
    entities: SelectType,
    fetch_first: bool,
    criteria: Criteria = None,
    clauses: list = None,
):
    is_scalar = False
    if not isinstance(entities, list):
        is_scalar = True
        entities = [entities]

    is_entity = not isinstance(entities[0], InstrumentedAttribute)
    query: Select = select(*entities)
    entity_type = entities[0] if is_entity else entities[0].class_
    query = build_where_statement(entity_type, query, criteria, clauses)
    if fetch_first:
        query = query.limit(1)

    async with begin_transaction(session):
        return await _query_and_unbind(session, query, is_scalar, is_entity, fetch_first)


def _build_column(table: Mapper, col: CriteriaKey) -> InstrumentedAttribute:
    return table.c[col] if isinstance(col, str) else col


def _build_clauses(entity: Type[Base], criteria: Criteria = None, existing_clauses: list = None):
    if not criteria and not existing_clauses:
        return []

    clauses = []

    table: Mapper = inspect(entity)

    if criteria:
        for col, values in criteria.items():
            where_col = _build_column(table, col)
            if isinstance(values, list):
                clauses.append(where_col.in_(values))
            elif values is None:
                clauses.append(where_col.is_(values))
            else:
                clauses.append(where_col == values)

    if existing_clauses:
        clauses += existing_clauses

    return clauses


async def _query_and_unbind(session: AsyncSession, query: Select, is_scalars: bool, is_entity: bool, fetch_first: bool):
    cursor_result: CursorResult = await session.execute(query)
    result = cursor_result
    if is_scalars:
        result = result.scalars()

    rows = []
    row = None

    if fetch_first:
        row = result.first()
    else:
        rows = result.all()

    if is_entity:
        _expunge(is_scalars, rows or [row], session)

    return rows or row


def _expunge(is_scalars: bool, rows: list, session: AsyncSession):
    for row in rows:
        if not row:
            continue

        entities = [row] if is_scalars else row

        for entity in entities:
            # unbind row so changes on it are not auto-flushed
            session.expunge(entity)
