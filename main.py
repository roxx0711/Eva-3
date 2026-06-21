import os
from dotenv import load_dotenv

from pymongo import MongoClient

import datetime
import subprocess 

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client: MongoClient = MongoClient(MONGO_URI)

try:
    print("Estableciendo conexión...⏳")
    client.admin.command("ping")
    print("Conexión establecida 😊")
except:
    print("❌ ERROR EN LA CONEXIÓN")
    exit(code=1)

db = client["ti3032_u3"]
collection = db["test"]