# files imports
from api.database import my_Base, engine
# Libs
from fastapi import FastAPI


# ------------------------------------
my_Base.metada.create_all(bind=engine)
my_app = FastAPI()

# check app
@my_app.get("/")
def read_root():
    return {"message":"Hello World"}


@my_app.post("/Register")
def sign_up():
    pass