import json

#Mongo
from dotenv import dotenv_values
from pymongo import MongoClient
from models import Serie
import json

#ENV Values
env = dotenv_values('.env')

# In case that there is an issue you need to activate the VirtualENV (VENV)
#Set-ExecutionPolicy Unrestricted -Scope Process

mongodb_client = MongoClient(env["ATLAS_URI"])
database = mongodb_client[env["DB_NAME"]]
print("Connected to the MongoDB database!")

serie = Serie(name="Prueba", season="Temporada 1", episode="Episodio 3")

serie.url = "https://example.com/"

new_serie1 = database["series"].insert_one(serie.__dict__)

created_serie1 = database["series"].find_one(
    {"_id": new_serie1.inserted_id}
)

print(created_serie1)

mongodb_client.close()