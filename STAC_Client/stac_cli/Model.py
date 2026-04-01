from pydantic import BaseModel, validator, Field
from typing import List, Dict, Literal, Optional


class Geometry(BaseModel):
    type: str
    coordinates: List[float]


class Asset(BaseModel):
    href: Optional[str] = None
    type: Optional[str] = None
    roles: Optional[List[str]] = None


class Properties(BaseModel):
    datetime: str
    title: Optional[str] = None
    description: Optional[str] = None


class STACItem(BaseModel):
    id: str
    type: Literal["Feature"] = "Feature"
    collection: str
    geometry: Geometry
    bbox: List[float]
    properties: Properties
    assets: Dict[str, Asset] = Field(default_factory=dict)

    @validator("assets")
    def validate_assets(cls, v):
        return v or {}