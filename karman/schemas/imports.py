from karman.schemas.base import ModelSchema


class CreateImport(ModelSchema):
    name: str
    # TODO: Support upload via URL (as a background task)


class Import(ModelSchema):
    id: int
    name: str
