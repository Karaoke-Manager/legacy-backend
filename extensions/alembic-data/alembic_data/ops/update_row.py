from typing import Any, Mapping, List

import sqlalchemy
from alembic.autogenerate import renderers
from alembic.autogenerate.api import AutogenContext
from alembic.operations import Operations, MigrateOperation

__all__ = ["UpdateRowOp"]

from sqlalchemy.sql.elements import ColumnClause


@Operations.register_operation("update_row")
class UpdateRowOp(MigrateOperation):
    """This `MigrationOperation` updates rows in a database table."""

    def __init__(self, table_name: str, new_values: Mapping[str, Any], old_values: Mapping[str, Any]) -> None:
        """Creates a new `InsertRowOp`.

        :param table_name: The name of the table to update values in.
        :param new_values: The new values to update in the table. Keys must correspond to column names in the table and
                           values to their values.
        :param old_values: The old values used to identify the row that should be updated.
        """
        self.table_name = table_name
        self.new_values = new_values
        self.old_values = old_values

    @classmethod
    def update_row(cls, operations: Operations, table_name: str, new_values: Mapping[str, Any],
                   old_values: Mapping[str, Any]):
        """Factory method for `UpdateRowOp`."""
        op = UpdateRowOp(table_name, new_values, old_values)
        return operations.invoke(op)

    def reverse(self) -> MigrateOperation:
        """Reverses the update operation by reverting back to the old values."""
        return UpdateRowOp(self.table_name, self.old_values, self.new_values)


@Operations.implementation_for(UpdateRowOp)
def update_row(operations: Operations, operation: UpdateRowOp) -> None:
    columns: List[ColumnClause] = [sqlalchemy.column(key) for key in operation.values.keys()]
    table = sqlalchemy.table(operation.table_name, *columns)
    where_clauses = [table.columns[key] == value for (key, value) in operation.old_values.items()]
    operations.execute(
        table.update().where(*where_clauses).values(**operation.new_values)
    )


@renderers.dispatch_for(UpdateRowOp)
def render_update_row(autogen_context: AutogenContext, op: UpdateRowOp) -> str:
    return "op.update_row(%r, **%r, **%r)" % (
        op.table_name,
        op.new_values,
        op.old_values
    )
