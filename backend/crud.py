from motor import motor_asyncio
import models
import auth
from config import get_config
from fastapi.encoders import jsonable_encoder


config = get_config()

client = motor_asyncio.AsyncIOMotorClient(config.database_url)
db = client.bgchecker

# crud functions are unsafe 
# i.e. a create doesn't check to see if obj already exists etc

async def get_user_by_email(email: str) -> models.User:
  if (user := await db["users"].find_one({"email": email})) is not None:
    return models.User.parse_obj(user)

async def create_user(user: models.UserCreate):
  hashed_password = auth.get_hash_from_str(user.password)
  user = models.User(name=user.name, email=user.email,hashed_password=hashed_password)
  user = jsonable_encoder(user)
  new_user = await db["users"].insert_one(user)
  created_user = await db["users"].find_one({"_id": new_user.inserted_id})

  return models.User.parse_obj(created_user)
