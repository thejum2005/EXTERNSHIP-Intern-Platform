import os


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")

    # Use database from environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ITEMS_PER_PAGE = int(os.environ.get("ITEMS_PER_PAGE", 10))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return config_by_name.get(env, DevelopmentConfig)