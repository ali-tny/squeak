# Squeak: quickly manipulate string SQL queries

String is King when it comes to SQL - no one wants to mess around constructing ad-hoc analytics 
queries as complicated Python objects. `squeak` is for speaking SQL: for when you want to make
simple changes to string SQL queries in Python without complicated string formatting, copy pasting
queries around, or writing `" AND ".join(where_clauses)`-style logic for the 300th time.
