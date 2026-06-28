import asyncio
from src.db import mongo

async def run():
    await mongo.connect()
    c = await mongo.get_logs_collection().count_documents({})
    print(f"Total Logs count: {c}")
    
    logs = await mongo.get_logs_collection().find().sort("timestamp", -1).limit(5).to_list(5)
    for l in logs:
        print(f"ID: {l['_id']}, User: {l.get('user_id')}, Type: {type(l.get('user_id'))}")

    await mongo.close()

asyncio.run(run())
