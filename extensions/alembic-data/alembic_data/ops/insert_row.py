from typing import Any, Mapping, List

import sqlalchemy
from alembic.autogenerate import renderers
from alembic.autogenerate.api import AutogenContext
from alembic.operations import Operations, MigrateOperation

__all__ = ["InsertRowOp"]

from sqlalchemy.sql.elements import ColumnClause


@Operations.register_operation("insert_row")
class InsertRowOp(MigrateOperation):
    """This `MigrationOperation` adds rows to a database table."""

    def __init__(self, table_name: str, **kwargs: Mapping[str, Any]) -> None:
        """Creates a new `InsertRowOp`.

        :param table_name: The name of the table to insert the row.
        :param kwargs: The values to insert into the table. Keys must correspond to column names in the table.
        """
        self.table_name = table_name
        self.values = kwargs

    @classmethod
    def insert_row(cls, operations: Operations, table_name: str, **kwargs: Mapping[str, Any]):
        """Factory method for `InsertRowOp`."""
        op = InsertRowOp(table_name, **kwargs)
        return operations.invoke(op)

    def reverse(self) -> MigrateOperation:
        """Reverses the insert row operation by deleting the respective row."""
        from .delete_row import DeleteRowOp
        return DeleteRowOp(self.table_name, **self.values)


@Operations.implementation_for(InsertRowOp)
def insert_row(operations: Operations, operation: InsertRowOp) -> None:
    columns: List[ColumnClause] = [sqlalchemy.column(key) for key in operation.values.keys()]
    table = sqlalchemy.table(operation.table_name, *columns)
    sql = table.insert().values(**operation.values)
    operations.execute(sql)


@renderers.dispatch_for(InsertRowOp)
def render_insert_row(autogen_context: AutogenContext, op: InsertRowOp) -> str:
    return "op.insert_row(%r, **%r)" % (
        op.table_name,
        op.values
    )
