from bson import ObjectId


def get_oid_validators():
    yield validate_object_id


def validate_object_id(value):
    return ObjectId(value)


def modify_oid_schema(field_schema):
    # TODO: Is this right?
    field_schema.update(
        type="string",
        length=24
    )


ObjectId.__get_validators__ = get_oid_validators
ObjectId.__modify_schema__ = modify_oid_schema

MongoID = ObjectId
