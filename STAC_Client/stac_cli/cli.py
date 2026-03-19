import click
from .Stac import STAC
from .Template import generate_item
import json



BASE_URL="http://localhost:8000"

@click.group()
def cli():
    """STAC CLI client"""
    pass

@cli.command()
def collections():

    client = STAC(BASE_URL)

    data = client.getcollections()

    print(json.dumps(data, indent=2))

@cli.command()
@click.argument("collection_id")
def items(collection_id):

    client = STAC(BASE_URL)

    data = client.get_items(collection_id)

    print(json.dumps(data, indent=2))

@cli.command()
@click.option("--token", required=True, help="Authentication token")
@click.option("--id", required=True, help="Item ID")
@click.option("--lon", required=True, type=float)
@click.option("--lat", required=True, type=float)
@click.option("--asset", required=True)
@click.option("--description", required=False)
def add_item(token, id, lon, lat, asset,description):

    client = STAC(BASE_URL, token)

    item = generate_item(
    id,
    "shared_collection",
    lon,
    lat,
    asset,
    description
)

    response = client.add_item("shared_collection", item)

    print(json.dumps(response, indent=2))
if __name__ == "__main__":
    cli()