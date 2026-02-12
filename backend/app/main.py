# from app.core import config 
from fastapi import FastAPI
from pydantic import BaseModel
# test
my_app = FastAPI()
@my_app.get("/")
def read_root():
    return {"message":"Hello World"}

@my_app.get("/items/{item_id}")
def read_item_id(item_id:int, q:str|None=None):
    return {"item_id" : item_id, "q" :q}

class Item(BaseModel):
    name : str
    price : float
    is_offer : bool | None = None

@my_app.put("/items/{item_id}")
def update_item(item_id : int, item: Item):
    return {"item_id": item_id, "item_name" : item.name}
# database
# engine==