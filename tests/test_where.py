import pytest

import squeak

QUERY = """
WITH x AS (
  SELECT *
  FROM y
)

SELECT *
FROM x
WHERE column = 4
"""


def _flatten(string: str) -> str:
    """Replace all whitespace in a string with spaces."""
    return " ".join(string.split())


def test_append_main():
    out = squeak.where(QUERY, "other_column = 1")

    expected = """
    WITH x AS (
      SELECT *
      FROM y
    )

    SELECT *
    FROM x
    WHERE column = 4
      AND other_column = 1
    """

    assert _flatten(out) == _flatten(expected)


def test_replace_main():
    out = squeak.where(QUERY, "other_column = 1", kind="replace")

    expected = """
    WITH x AS (
      SELECT *
      FROM y
    )

    SELECT *
    FROM x
    WHERE other_column = 1
    """

    assert _flatten(out) == _flatten(expected)


def test_append_cte():
    expected = """
    WITH x AS (
      SELECT *
      FROM y
      WHERE some_column = 3
    )

    SELECT *
    FROM x
    WHERE column = 4
    """

    appended = squeak.where(QUERY, "some_column = 3", cte="x")
    assert _flatten(appended) == _flatten(expected)
    # The subquery has no filter, so replacing and appending is equivalent
    replaced = squeak.where(QUERY, "some_column = 3", cte="x", kind="replace")
    assert _flatten(replaced) == _flatten(expected)


EXTRAS = [
    "GROUP BY 1, 2, 3",
    "HAVING COUNT(*) > 2",
    "WINDOW w AS (PARTITION BY id ORDER BY y)",
    "ORDER BY 3 DESC",
    "LIMIT 10",
    "OFFSET 10",
    "FETCH FIRST 20 ROWS ONLY",
    "FOR UPDATE",
]


@pytest.mark.parametrize("extra", EXTRAS)
@pytest.mark.parametrize(
    "query, expected, cte",
    [
        ("SELECT * FROM x {extra}", "SELECT * FROM x WHERE z {extra}", None),
        (
            "WITH x AS (SELECT * FROM y {extra}) SELECT * FROM x",
            "WITH x AS (SELECT * FROM y WHERE z {extra}) SELECT * FROM x",
            "x",
        ),
    ],
)
def test_other_options(extra, query, expected, cte):
    out = squeak.where(query.format(extra=extra), clause="z", cte=cte)

    assert _flatten(out) == _flatten(expected.format(extra=extra))


def test_raises_multiple_statements():
    with pytest.raises(ValueError):
        squeak.where("SELECT * FROM x; SELECT * FROM y", clause=None)


def test_raises_union():
    query = "WITH x AS (SELECT * FROM y) SELECT * FROM x UNION SELECT * FROM z"

    # Let it run for the subquery, which contains no UNION
    squeak.where(query, "some_column = 3", cte="x")
    with pytest.raises(ValueError):
        # But fail for the main query, since it doesn't know where to put the WHERE
        squeak.where(query, "some_column = 3")
