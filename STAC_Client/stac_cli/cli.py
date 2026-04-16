import click
import json
import os
import uuid
from datetime import datetime, timezone
from .Stac import STAC
from .Template import create_item_template,validate_item

BASE_URL = "https://api.eneslab.pilot.eosc-beyond.eu/"


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
    
    token = resolve_token(token)
    client = STAC(BASE_URL, token)
    
    with open(file_path, "r", encoding="utf-8") as f:
        item = json.load(f)

   

    item["id"] = str(uuid.uuid4())
    item.setdefault("properties", {})
    item["properties"]["datetime"] = datetime.now(timezone.utc).isoformat()
    item.setdefault("links", [])

    try:
        validate_item(item)
        response = client.add_item(collection_id, item)
        if "detail" in response:
            for err in response["detail"]:
                print(err.get("msg"))
            return
        #print(json.dumps(response, indent=2))
        print(f"Item added to {collection_id}")
    except ValueError as e:
        print(f"Item not added:")

@items.command("create_template")
@click.option("--output", default="item_template.json")
def create_template_cmd(output):
    create_item_template(output)


@stac_cli.group()
def auth():
    pass

def resolve_token(cli_token):
    token = cli_token or os.getenv("TOKEN")
    if not token:
        raise ValueError("Token not provided. Use --token or export TOKEN.")
    return token

@auth.command("verify")
@click.option("--token", required=False)
def verify_token(token):
    try:
        token = resolve_token(token)
        client = STAC("https://aai-demo.egi.eu")

        result = client.verify_token(token)

        if result:
            print("Token Valid")
        else:
            print("Token Invalid")

    except ValueError as e:
        print(e)



if __name__ == "__main__":
    stac_cli()