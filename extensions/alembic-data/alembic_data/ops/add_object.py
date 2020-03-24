import sqlalchemy
from alembic.autogenerate import renderers
from alembic.autogenerate.api import AutogenContext
from alembic.operations import Operations, MigrateOperation

__all__ = ["AddObjectOp", "add_object", "render_add_object"]


@Operations.register_operation("add_object")
class AddObjectOp(MigrateOperation):
    def __init__(self, table_name: str, **kwargs):
        self.table_name = table_name
        self.values = kwargs

    @classmethod
    def add_object(cls, operations: Operations, table_name: str, **kwargs):
        op = AddObjectOp(table_name, **kwargs)
        return operations.invoke(op)

    def reverse(self):
        from .delete_object import DeleteObjectOp
        return DeleteObjectOp(self.table_name, **self.values)


@Operations.implementation_for(AddObjectOp)
def add_object(operations: Operations, operation: AddObjectOp):
    columns = [sqlalchemy.column(key) for key in operation.values.keys()]
    table = sqlalchemy.table(operation.table_name, *columns)
    sql = table.insert().values(**operation.values)
    operations.execute(sql)


@renderers.dispatch_for(AddObjectOp)
def render_add_object(autogen_context: AutogenContext, op: AddObjectOp):
    return "op.add_object(%r, **%r)" % (
        op.table_name,
        op.values
    )
