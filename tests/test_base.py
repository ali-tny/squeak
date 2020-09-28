import pytest

import sqlparse

from squeak import base


def test_choose_cte_raises_missing_cte():
    with pytest.raises(ValueError):
        base.choose_cte(sqlparse.parse("WITH x AS (SELECT * FROM y) SELECT * FROM x")[0], cte="z")


cte_queries = [
    "WITH x AS (SELECT * FROM y)",
    "WITH x AS (SELECT * FROM y), y AS (SELECT * FROM z)",
    "WITH y AS (SELECT * FROM z), x AS (SELECT * FROM y)",
]


@pytest.mark.parametrize("query", cte_queries)
def test_choose_cte(query):
    cte, location = base.choose_cte(sqlparse.parse(query)[0], cte="x")
    assert str(cte) == "(SELECT * FROM y)"


@pytest.mark.parametrize("query", cte_queries)
def test_replace_cte(query):
    _, location = base.choose_cte(sqlparse.parse(query)[0], cte="x")
    replacement, _ = base.choose_cte(
        sqlparse.parse("WITH replacement AS (COMPLETELY DIFFERENT)")[0], cte="replacement"
    )
    parsed = base.replace_inner_statement_by_location(
        sqlparse.parse(query)[0], replacement, location
    )
    assert str(base.choose_cte(parsed, cte="x")[0]) == "(COMPLETELY DIFFERENT)"
