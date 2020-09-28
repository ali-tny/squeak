from typing import Optional, Tuple
from typing_extensions import Literal

import sqlparse

from . import base

AFTER_WHERE_KEYWORDS = [
    "GROUP BY",
    "HAVING",
    "WINDOW",
    "ORDER BY",
    "LIMIT",
    "OFFSET",
    "FETCH",
    "FOR",
]


def where(
    query: str, clause: str, cte: str = None, kind: Literal["append", "replace"] = "append"
) -> str:
    """Append (with AND) or replace WHERE filters in a query.

    :param query: SQL query
    :param clause: string clause to be appended with AND - eg "col_1 = 3 OR col_2 = 4"
    :param cte: the string name of a subquery to modify, or cte=None to modify the main SELECT.
        Default is None.
    :param kind: "append": append the clause to the existing clauses with AND, or
        "replace" replace the the whole WHERE clause (if it exists)
    """
    parsed_statements = sqlparse.parse(query)
    if len(parsed_statements) > 1:
        raise ValueError("More than 1 statement in query.")
    parsed = parsed_statements[0]
    if cte:
        statement, indices = base.choose_cte(parsed, cte)
        filtered_statement = _add_filter_to_statement(statement, clause, kind)
        parsed = base.replace_inner_statement_by_location(parsed, filtered_statement, indices)
    else:
        parsed = _add_filter_to_statement(parsed, clause, kind)
    return str(parsed)


def _add_filter_to_statement(
    statement: sqlparse.sql.Statement, clause: str, kind: Literal["append", "replace"]
) -> sqlparse.sql.Statement:
    for t in statement.tokens:
        if t.ttype == sqlparse.tokens.Token.Keyword and t.value.lower() == "union":
            raise ValueError("Statement includes a UNION (don't know which table to filter)")

    where, where_idx = _find_where(statement)
    full_clause = f" {where} AND {clause} " if where and kind == "append" else f" WHERE {clause} "
    where_statement = sqlparse.parse(full_clause)[0]

    if where:
        statement.tokens[where_idx] = where_statement
    else:
        tokens = statement.tokens[:where_idx] + [where_statement] + statement.tokens[where_idx:]
        statement.tokens = tokens
    return statement


def _find_where(statement: sqlparse.sql.Statement) -> Tuple[Optional[sqlparse.sql.Statement], int]:
    for idx, token in enumerate(statement.tokens):
        if type(token) is sqlparse.sql.Where:
            return token, idx
        if token.ttype == sqlparse.tokens.Token.Keyword and token.value in AFTER_WHERE_KEYWORDS:
            return None, idx - 1
    # If we didn't find a WHERE or anything that should go after it, stick it at the end,
    # but before a final closing parenthesis
    return (None, idx) if token.value == ")" else (None, idx + 1)
