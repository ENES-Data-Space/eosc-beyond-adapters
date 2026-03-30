import click
import json
import uuid
from datetime import datetime, timezone
from .Stac import STAC
from .Template import create_item_template,validate_item

BASE_URL = "http://localhost:8000"


@click.group()
def stac_cli():
    pass



@stac_cli.group()
def collections():
    pass


@collections.command("get")
@click.option("--collection_id", required=False)
def get_collections(collection_id):
    client = STAC(BASE_URL)

    if collection_id:
        data = client.getcollection(collection_id)
    else:
        data = client.getcollections()

    print(json.dumps(data, indent=2))



@stac_cli.group()
def items():
    pass


@items.command("get")
@click.option("--collection_id", required=True)
@click.option("--item_id", required=False)
def get_items(collection_id, item_id):
    client = STAC(BASE_URL)

    if item_id:
        data = client.get_item(collection_id, item_id)
    else:
        data = client.get_items(collection_id)

    print(json.dumps(data, indent=2))


@items.command("add")
@click.option("--collection_id", required=True)
@click.option("--token", required=True)
@click.option("--file", "file_path", required=True)
def add_item(collection_id, token, file_path):
    client = STAC(BASE_URL, token)


    with open(file_path, "r", encoding="utf-8") as f:
        item = json.load(f)

   

    item["id"] = str(uuid.uuid4())
    item.setdefault("properties", {})
    item["properties"]["datetime"] = datetime.now(timezone.utc).isoformat()

    response = client.add_item(collection_id, item)

    print(json.dumps(response, indent=2))
    print(f"Item Added to {collection_id}")

@items.command("create_template")
@click.option("--output", default="item_template.json")
def create_template_cmd(output):
    create_item_template(output)


@stac_cli.group()
def auth():
    pass


@auth.command("verify")
@click.option("--token", required=True)
def verify_token(token):
    client = STAC("https://aai-demo.egi.eu")
    result = client.verify_token(token)
    if result:
        print("Token Valid")
    else : 
        print("Token Invalid")



if __name__ == "__main__":
    stac_cli()