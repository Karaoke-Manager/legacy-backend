from pydantic import BaseModel

from karman.config import app_config
from karman.helpers.mongo import MongoID


def to_camel_case(string: str):
    components = string.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


class BaseSchema(BaseModel):
    class Config:
        # Get some extra performance in production by disabling these validations
        validate_all = app_config.debug
        validate_assignment = app_config.debug
        allow_population_by_field_name = True
        alias_generator = to_camel_case


class ModelSchema(BaseSchema):
    id: MongoID

    class Config(BaseSchema.Config):
        orm_mode = True
        json_encoders = {MongoID: str}
