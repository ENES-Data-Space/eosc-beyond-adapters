from .Model import STACItem, Geometry, Asset, Properties
from datetime import datetime
import uuid
from pathlib import Path
import json

def create_item_template(output_dir: str="item_template.json"):
    template = {
        "type": "Feature",
        "stac_version": "1.0.0",
        "collection": "shared_collection",
        "geometry": {
            "type": "Polygon",
            "coordinates": 
            [
                    [
                        [-180, -90],
                        [180, -90],
                        [180, 90],
                        [-180, 90],
                        [-180, -90]
                    ]
                    ]
                },
        "bbox": [-180, -90, 180, 90],
        "properties": {
            "owner": "",
            "description": "",
            "title": "",
            "pid": "Optional"
        },
        "assets": {
            "data": {
                "href": "Asset href is required and cannot be empty. You may use 'assets': {} if no asset is provided.",
                "type": "application/json",
                "title": "Main asset"
            }
        }
    }

    output_file = Path(output_dir)
    with open(output_file,"w",encoding="utf-8") as f:
        json.dump(template,f,indent=2)
    print(f"Template Created at {output_file.resolve()}")

def validate_item (item : dict):
    required_fields = ["type", "geometry", "bbox", "properties", "assets"]

    for field in required_fields:
        if field not in item:
            raise ValueError(f"Missing required field :{field}")
    
    if item["type"] != "Feature":
        raise ValueError("Stac item type must be Feature")
    
    