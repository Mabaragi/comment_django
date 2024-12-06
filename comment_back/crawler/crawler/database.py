# app/database.py

import motor.motor_asyncio
import os
from bson.objectid import ObjectId


class MongoDB:
    def __init__(self, mongo_uri: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        self.db = self.client.get_database("my_project")
