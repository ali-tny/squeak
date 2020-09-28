from typing import Optional, Tuple, Type

import sqlparse

Statement = Type[sqlparse.sql.Statement]
Location = Tuple[int, ...]


def choose_cte(parsed: Statement, cte: str) -> Tuple[Statement, Location]:
    """Return a given named CTE and its location in a parsed query.

    The returned statement will be a SELECT statement that could be executed by itself. The
    location of the returned statement in the original parsed statement is given as a tuple of
    indices of the "tree" of token attributes of the parsed statement.

    See base.replace_inner_statement_by_location to replace a statement given this location.

    :param parsed: a SQL statement parsed by sqlparse
    :param cte: the string name of the CTE to return
    """
    token, indices = _search_tree_for_cte(parsed, cte)
    if token and indices:
        return token, indices
    raise ValueError(f"CTE {cte} not found in query")


def replace_inner_statement_by_location(
    parsed: Statement, replacement: Statement, location: Location
) -> Statement:
    """Replace a part of a statement, given it's location (ie tuple of indices of the tree).

    :param parsed: the statement to replace within
    :param replacement: the replacement statement (should be exactly the same form as the one being
        replaced)
    :param location: the tuple of indices representing the inner statement's location in the tree
    """
    statement = parsed
    for idx in location[:-1]:
        statement = statement.tokens[idx]
    statement.tokens[location[-1]] = replacement
    return parsed


def _search_tree_for_cte(
    tree: Statement, cte: str, wait_for_keyword: bool = True
) -> Tuple[Optional[Statement], Optional[Location]]:
    """Walk the tree representing a parsed SQL statement looking for a named CTE.

    Returns the Statement representing the CTE and a tuple of indices representing it's location in
    the tree. Note that we only branch at IdentifierLists and consider Identifiers as leaf nodes -
    so we only will consider non-nested CTEs.

    :param tree: a statement parsed by sqlparse to search
    :param cte: the name of the CTE
    :wait for keyword: default: only consider identifiers that follow the CTE keyword, otherwise
        False to consider _all_ identifiers (like we would in an IdentifierList of CTEs)
    """
    check_next_identifier = not wait_for_keyword
    for idx, token in enumerate(tree.tokens):
        if token.ttype == sqlparse.tokens.Keyword.CTE:
            check_next_identifier = True
        if check_next_identifier and type(token) == sqlparse.sql.Identifier:
            inner_token, inner_idx = _get_cte_from_token(token, cte)
            if inner_token and inner_idx:
                return inner_token, (idx, inner_idx)
            check_next_identifier = not wait_for_keyword
        if check_next_identifier and type(token) == sqlparse.sql.IdentifierList:
            inner_token, indices = _search_tree_for_cte(token, cte, wait_for_keyword=False)
            if inner_token and indices:
                return inner_token, (idx,) + indices
    return None, None


def _get_cte_from_token(
    identifier: sqlparse.sql.Identifier, cte: str
) -> Tuple[Optional[Statement], Optional[int]]:
    if _get_name(identifier) == cte:
        for inner_idx, inner_token in enumerate(identifier.tokens):
            if type(inner_token) == sqlparse.sql.Parenthesis:
                return inner_token, inner_idx
    return None, None


def _get_name(identifier: sqlparse.sql.Identifier) -> str:
    for token in identifier.tokens:
        if token.ttype == sqlparse.tokens.Name:
            return token.value
    raise ValueError(f"Identifier {identifier} has no name")
