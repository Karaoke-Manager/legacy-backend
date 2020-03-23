import sqlalchemy
from alembic.autogenerate import renderers
from alembic.autogenerate.api import AutogenContext
from alembic.operations import Operations, MigrateOperation

__all__ = ["DeleteObjectOp", "delete_object", "render_delete_object"]

from sqlalchemy import and_


@Operations.register_operation("delete_object")
class DeleteObjectOp(MigrateOperation):
    def __init__(self, table_name: str, **kwargs):
        self.table_name = table_name
        self.values = kwargs

    @classmethod
    def delete_object(cls, operations, table_name: str, **kwargs):
        op = DeleteObjectOp(table_name, **kwargs)
        return operations.invoke(op)

    def reverse(self):
        from flask_data.ops.add_object import AddObjectOp
        return AddObjectOp(self.table_name, **self.values)


@Operations.implementation_for(DeleteObjectOp)
def delete_object(operations, operation: DeleteObjectOp):
    columns = [sqlalchemy.column(key) for key in operation.values.keys()]
    table = sqlalchemy.table(operation.table_name, *columns)
    where_clauses = [table.columns[key] == value for (key, value) in operation.values.items()]
    sql = table.delete().where(and_(*where_clauses))
    operations.execute(sql)


@renderers.dispatch_for(DeleteObjectOp)
def render_delete_object(autogen_context: AutogenContext, op: DeleteObjectOp):
    return "op.delete_object(%r, **%r)" % (
        op.table_name,
        op.values
    )
