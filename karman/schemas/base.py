from pydantic import BaseModel


def to_camel_case(string: str):
    components = string.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


class BaseSchema(BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True


class ModelSchema(BaseSchema):
    class Config:
        orm_mode = True
