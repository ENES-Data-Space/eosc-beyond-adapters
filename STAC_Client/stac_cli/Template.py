from .Model import STACItem, Geometry, Asset, Properties
from datetime import datetime


def generate_item(
    item_id,
    collection,
    lon,
    lat,
    asset_link,
    description: str | None = None
):

    item = STACItem(
        id=item_id,
        type="Feature",
        collection=collection,
        geometry=Geometry(
            type="Point",
            coordinates=[lon, lat]
        ),
        bbox=[lon, lat, lon, lat],
        properties=Properties(
            datetime=datetime.utcnow().isoformat() + "Z",
            title=item_id,
            description=description
        ),
        assets={
            "data": Asset(
                href=asset_link,
                type="application/vnd+zarr",
                roles=["data"]
            )
        },
        links=[]
    )

    return item.model_dump()