import pytest

import sqlparse

from squeak import base


def test_choose_cte_raises_missing_cte():
    with pytest.raises(ValueError):
        base.choose_cte(sqlparse.parse("WITH x AS (SELECT * FROM y) SELECT * FROM x")[0], cte="z")
