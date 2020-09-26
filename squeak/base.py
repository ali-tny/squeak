from typing import Tuple

import sqlparse


def choose_cte(
    parsed: sqlparse.sql.Statement, cte: str = None
) -> Tuple[sqlparse.sql.Statement, int, int]:
    """Return a given named CTE and its index and subindex in a parsed query.

    The returned statement will be a SELECT statement that could be executed by itself. The
    location of the returned statement in the original parsed statement is
    `parsed.tokens[idx].tokens[inner_idx]`.

    :param parsed: a SQL statement parsed by sqlparse
    :param cte: the string name of the CTE to return
    """
    check_next_identifier = False
    for idx, token in enumerate(parsed.tokens):
        if token.ttype == sqlparse.tokens.Keyword.CTE:
            check_next_identifier = True
        if check_next_identifier and type(token) == sqlparse.sql.Identifier:
            cte_name = _get_name(token)
            if cte_name == cte:
                for inner_idx, inner_token in enumerate(token.tokens):
                    if type(inner_token) == sqlparse.sql.Parenthesis:
                        return inner_token, idx, inner_idx
            check_next_identifier = False
    raise ValueError(f"CTE {cte} not found in query")


def _get_name(identifier: sqlparse.sql.Identifier) -> str:
    for token in identifier.tokens:
        if token.ttype == sqlparse.tokens.Name:
            return token.value
    raise ValueError(f"Identifier {identifier} has no name")
