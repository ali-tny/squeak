# Squeak: quickly manipulate string SQL queries

String is King when it comes to SQL - no one wants to mess around constructing ad-hoc analytics 
queries as complicated Python objects. `squeak` is for speaking SQL: for when you want to make
simple changes to string SQL queries in Python without complicated string formatting, copy pasting
queries around, or writing `" AND ".join(where_clauses)`-style logic for the 300th time.

```python
>>> query = """
... WITH subquery_1 AS (
...   SELECT DISTINCT ON (id) *
...   FROM y
...   ORDER BY id, created_at DESC
... )
...
... SELECT * FROM subquery_1
... WHERE col_1 = 3
... """
>>> with_added_filter = squeak.where(query, "col_2 = 'hey'")
>>> print(with_added_filter)

WITH subquery_1 AS (
  SELECT DISTINCT ON (id) *
  FROM y
  ORDER BY id, created_at DESC
)

SELECT * FROM subquery_1
 WHERE col_1 = 3
 AND col_2 = 'hey'

>>> with_replaced_filter = squeak.where(query, "col_2 = 'hey'", kind="replace")
>>> print(with_replaced_filter)

WITH subquery_1 AS (
  SELECT DISTINCT ON (id) *
  FROM y
  ORDER BY id, created_at DESC
)

SELECT * FROM subquery_1
 WHERE col_2 = 'hey'

>>> with_filter_on_subquery = squeak.where(query, "col_2 = 'hey'", cte="subquery_1")
>>> print(with_filter_on_subquery)

WITH subquery_1 AS (
  SELECT DISTINCT ON (id) *
  FROM y
  WHERE col_2 = 'hey'  ORDER BY id, created_at DESC
)

SELECT * FROM subquery_1
WHERE col_1 = 3
```
