from typing import Any, Mapping, List

import sqlalchemy
from alembic.autogenerate import renderers
from alembic.autogenerate.api import AutogenContext
from alembic.operations import Operations, MigrateOperation
from sqlalchemy import and_

__all__ = ["DeleteRowOp"]

from sqlalchemy.sql.elements import ColumnClause


@Operations.register_operation("delete_row")
class DeleteRowOp(MigrateOperation):
    """This `MigrationOperation` deletes a rows from a database table."""

    def __init__(self, table_name: str, **kwargs: Mapping[str, Any]) -> None:
        """Creates a new `DeleteRowOp`.

        :param table_name: The name of the table to delete the row from.
        :param kwargs: The values used to identify the exact row. Keys must correspond to column names in the table and
                       values to their values.
        """
        self.table_name = table_name
        self.values = kwargs

    @classmethod
    def delete_row(cls, operations: Operations, table_name: str, **kwargs: Mapping[str, Any]):
        """Factory method for `DeleteRowOp`."""
        op = DeleteRowOp(table_name, **kwargs)
        return operations.invoke(op)

    def reverse(self) -> MigrateOperation:
        """Reverses the insert row operation by inserting the respective row."""
        from .insert_row import InsertRowOp
        return InsertRowOp(self.table_name, **self.values)


@Operations.implementation_for(DeleteRowOp)
def delete_row(operations, operation: DeleteRowOp) -> None:
    columns: List[ColumnClause] = [sqlalchemy.column(key) for key in operation.values.keys()]
    table = sqlalchemy.table(operation.table_name, *columns)
    where_clauses = [table.columns[key] == value for (key, value) in operation.values.items()]
    sql = table.delete().where(and_(*where_clauses))
    operations.execute(sql)


@renderers.dispatch_for(DeleteRowOp)
def render_delete_row(autogen_context: AutogenContext, op: DeleteRowOp) -> str:
    return "op.delete_row(%r, **%r)" % (
        op.table_name,
        op.values
    )
