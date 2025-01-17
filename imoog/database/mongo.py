from __future__ import annotations

from typing import Tuple

from motor.motor_asyncio import (
    AsyncIOMotorCollection,
    AsyncIOMotorClient
)

from .drivers import Driver # import the base driver impl


class MongoDriver(Driver):
    async def connect(self, **kwargs):
        self.identifier = "mongo"

        connection_uri = kwargs["connection_uri"]
        database_name = kwargs["database_name"]
        collection_name = kwargs["collection_name"]

        client = AsyncIOMotorClient(connection_uri)
        _db = client[database_name]
        coll = _db[collection_name]
        self._connection: AsyncIOMotorCollection = coll

        # custom attributes
        self._parent_client = client
        return self._connection
    
    async def insert(
        self,
        image: bytes,
        name: str,
        mime: str
    ):
        insert = {
            "_id": name,
            "image": image,
            "mime": mime
        }
        await self._connection.insert_one(insert)
        return 0

    async def fetch(
        self,
        name: str
    ) -> Tuple[bytes, str]:
        query = {"_id": name}
        result = await self._connection.find_one(query)
        image = result["image"]
        mime = result["mime"]
        decompressed = self.decompress(image)
        return (decompressed, mime)

    async def cleanup(self):
        return self._parent_client.close()

_DRIVER = MongoDriver
_DRIVER_TYPE = "MONGO"