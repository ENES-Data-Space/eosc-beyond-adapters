from pydantic import BaseModel
from typing import List,Dict, Literal,Optional

class Geometry(BaseModel):
    type: str 
    coordinates :List[float]

class Asset(BaseModel):
    href : str
    type : str 
    roles : List[str]

class Properties(BaseModel):
    datetime : str
    title: Optional[str] = None
    description: Optional[str] = None

class STACItem(BaseModel):
    id : str
    type : Literal["Feature"] = "Feature" 
    collection: str
    geometry: Geometry
    bbox: List[float]
    properties: Properties
    assets: Dict[str, Asset]
    links: List = []