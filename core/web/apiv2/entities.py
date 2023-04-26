import datetime
from typing import Iterable

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.schemas import entity


# Request schemas
class NewEntityRequest(BaseModel):
    entity: entity.EntityTypes

class EntitySearchRequest(BaseModel):
    name: str | None = None
    type: entity.EntityType | None = None
    count: int = 50
    page: int = 0

class EntitySearchResponse(BaseModel):
    entities: list[entity.Entity]
    total: int

# API endpoints
router = APIRouter()

@router.get('/')
async def entities_root() -> Iterable[entity.Entity]:
    return entity.Entity.list()

@router.post('/')
async def new(request: NewEntityRequest) -> entity.Entity:
    """Creates a new entity in the database."""
    new = request.entity.save()
    return new

@router.get('/{entity_id}')
async def details(entity_id) -> entity.EntityTypes:
    """Returns details about an observable."""
    db_entity: entity.EntityTypes = entity.Entity.get(entity_id)  # type: ignore
    if not db_entity:
        raise HTTPException(status_code=404, detail="entity not found")
    return db_entity
