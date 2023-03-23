from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.schemas.entity import Entity
from core.schemas.graph import Relationship
from core.schemas.observable import TYPE_MAPPING, Observable

# Requequest schemas

class GraphDirection(str, Enum):
    outbound = 'outbound'
    inbound = 'inbound'
    any = 'any'

class GraphSearchRequest(BaseModel):
    source: str
    link_type: str | None
    hops: int
    direction: GraphDirection
    include_original: bool

class GraphAddRequest(BaseModel):
    source: str
    target: str
    link_type: str
    description: str

class GraphSearchResponse(BaseModel):
    vertices: dict[str, Observable | Entity]
    edges: list[Relationship]


# API endpoints
router = APIRouter()

@router.post('/search')
async def search(request: GraphSearchRequest) -> GraphSearchResponse:
    """Fetches neighbros for a given Yeti Object."""
    object_type, object_id = request.source.split('/')
    if object_type not in TYPE_MAPPING:
        raise HTTPException(status_code=400, detail='Invalid object type')
    yeti_object = TYPE_MAPPING[object_type].get(object_id)
    if not yeti_object:
        raise HTTPException(
            status_code=404, detail=f'Source object {request.source} not found')
    neighbors = yeti_object.neighbors(
        link_type=request.link_type,
        direction=request.direction,
        include_original=request.include_original,
        hops=request.hops,
    )
    return neighbors

@router.post('/add')
async def add(request: GraphAddRequest) -> Relationship:
    """Adds a link to the graph."""
    source_type, source_id = request.source.split('/')
    target_type, target_id = request.target.split('/')

    if source_type not in TYPE_MAPPING:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid source object type: {source_type}')
    if target_type not in TYPE_MAPPING:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid target object type: {target_type}')

    source_object = TYPE_MAPPING[source_type].get(source_id)
    target_object = TYPE_MAPPING[target_type].get(target_id)
    if source_object is None:
        raise HTTPException(
            status_code=404,
            detail=f'Source object {request.source} not found')
    if target_object is None:
        raise HTTPException(
            status_code=404,
            detail=f'Target object {request.target} not found')

    relationship = source_object.link_to(
        target_object, request.link_type, request.description)
    return relationship

@router.delete('/{relationship_id}')
async def delete(relationship_id: str) -> None:
    """Deletes a link from the graph."""
    relationship = Relationship.get(relationship_id)
    if relationship is None:
        raise HTTPException(
            status_code=404,
            detail=f'Relationship {relationship_id} not found')
    relationship.delete()
