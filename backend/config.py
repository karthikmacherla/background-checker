import os
from dotenv import load_dotenv, dotenv_values

config_obj = None


class Config:
    google_client_id: str
    jwt_secret: str
    hash_algo: str
    access_token_expire_minutes: int
    database_url: str
    log_loc: str = "../server1.log"
    s3_bucket_loc: str


def get_config():
    """Sets up configuration for the app"""
    global config_obj
    if config_obj:
        return config_obj
    config = {
        **dotenv_values(".env"),  # load development variables first
        **os.environ,  # override loaded values with environment variables
    }
    config_obj = Config()
    config_obj.google_client_id = config.get("GOOGLE_CLIENT_ID")
    config_obj.jwt_secret = config.get("JWT_SECRET")
    config_obj.hash_algo = config.get("ALGORITHMS")
    config_obj.access_token_expire_minutes = int(config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
    config_obj.database_url = config.get("DATABASE_URL")
    config_obj.s3_bucket_loc = config.get("S3BUCKET_URL")
    config_obj.log_loc = config.get("LOGGER_PATH", config_obj.log_loc)
    return config_obj
