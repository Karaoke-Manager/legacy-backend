import sqlalchemy
from alembic.autogenerate import renderers
from alembic.autogenerate.api import AutogenContext
from alembic.operations import Operations, MigrateOperation

__all__ = ["UpdateObjectOp", "update_object", "render_update_object"]


@Operations.register_operation("update_object")
class UpdateObjectOp(MigrateOperation):
    def __init__(self, table_name: str, new_values: dict, old_values: dict):
        self.table_name = table_name
        self.new_values = new_values
        self.old_values = old_values

    @classmethod
    def update_object(cls, operations, table_name: str, new_values: dict, old_values: dict):
        op = UpdateObjectOp(table_name, new_values, old_values)
        return operations.invoke(op)

    def reverse(self):
        return UpdateObjectOp(self.table_name, self.old_values, self.new_values)


@Operations.implementation_for(UpdateObjectOp)
def update_object(operations, operation: UpdateObjectOp):
    columns = [sqlalchemy.column(key) for key in operation.values.keys()]
    table = sqlalchemy.table(operation.table_name, *columns)
    where_clauses = [table.columns[key] == value for (key, value) in operation.old_values.items()]
    sql = table.update().where(*where_clauses).values(**operation.new_values)
    operations.execute(sql)


@renderers.dispatch_for(UpdateObjectOp)
def render_update_object(autogen_context: AutogenContext, op: UpdateObjectOp):
    return "op.update_object(%r, **%r, **%r)" % (
        op.table_name,
        op.new_values,
        op.old_values
    )
