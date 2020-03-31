import abc

from pydantic import BaseModel, root_validator


class CaseInsensitiveSchema(BaseModel, abc.ABC):
    class Config:
        case_sensitive = False

    @root_validator(pre=True)
    def lower_keys(cls, values: dict):
        return {key.lower(): value for (key, value) in values.items()}
