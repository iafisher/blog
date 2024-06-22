# Using SQLite effectively in Python
I use [SQLite](https://sqlite.org/index.html) as the database for my personal projects in Python. It is [lightweight](https://sqlite.org/serverless.html), [reliable](https://sqlite.org/hirely.html), [well-documented](https://sqlite.org/lang.html), and [better than the filesystem](https://sqlite.org/appfileformat.html) for persistent storage. I'd like to share a few lessons I have learned on using SQLite effectively in Python.

The official documentation for Python's `sqlite3` module already has a section on ["Using `sqlite3` efficiently"](https://docs.python.org/3/library/sqlite3.html#using-sqlite3-efficiently). It's worth reading that first, as this post covers different topics.


## Turn on foreign key enforcement
Foreign key constraints are not enforced by default in SQLite. If you want the database to prevent you from inserting invalid foreign keys, then you must run `PRAGMA foreign_keys = 1` to turn enforcement on. Note that this pragma command must be run **outside of a transaction**; if you run it while a transaction is active, it will [silently do nothing](https://sqlite.org/pragma.html#pragma_foreign_keys).

Since I prefer for my database to detect invalid foreign keys for me, and since (as we'll see below) the Python's `sqlite3` module will sometimes open transactions implicitly, I run `PRAGMA foreign_keys = 1` right after I open the connection to the database.


## Manage your transactions explicitly
By default, the underlying SQLite library operates in `autocommit` mode, in which changes are committed immediately unless a transaction has been opened with `BEGIN` or `SAVEPOINT`. You can verify this by opening the same database file with the `sqlite3` command-line shell in two different terminals at the same time, and observing that, e.g., a row inserted in one terminal will be returned by a `SELECT` statement run in the other. Once you open a transaction with `BEGIN`, however, subsequent changes will *not* be visible to the other terminal until you commit the transaction with `COMMIT`.

Python's `sqlite3` module [does not](https://docs.python.org/3/library/sqlite3.html#controlling-transactions) operate in `autocommit` mode. Instead, it will start a transaction before data manipulation language (DML) statements[^dml] such as `INSERT` and `UPDATE`, and, until Python 3.6, data definition language (DDL) statements such as `CREATE TABLE`.

Opening a transaction in SQLite has several implications:

1. You will not be able to open a transaction in the same process with `BEGIN`.
2. You will not be able to open a write transaction in a different process, since by default SQLite only allows [one write transaction at a time](https://sqlite.org/lang_transaction.html).
3. You will not be able to enable or disable foreign key constraint enforcement.

These consequences can come as a surprise when `sqlite3` has silently opened a transaction without your knowledge. Even worse, the `Connection.close` method [will not commit an open transaction](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.close), so you have to manually commit the transaction that `sqlite3` automatically opened.

I prefer to manage my transactions explicitly. To do so, pass `isolation_level=None` as an argument to `sqlite3.connect`, which will leave the database in the default `autocommit` mode and allow you to issue `BEGIN`, `COMMIT`, and `ROLLBACK` statements yourself.


## Use adapters and converters (with caution)
Python's `sqlite3` module allows you to register **adapters** to convert Python objects to SQLite values, and **converters** to convert SQLite values to Python objects (based on the type of the column). `sqlite3` [automatically registers](https://docs.python.org/3/library/sqlite3.html#default-adapters-and-converters) converters for `DATE` and `TIMESTAMP` columns, and corresponding adapters for Python `date` and `datetime` objects. Adapters are enabled by default, while converters must be explicitly enabled with the `detect_types` parameter to `sqlite3.connect`.

In addition to the default converters, I register my own for `DECIMAL`, `BOOLEAN`, and `TIME` columns, to convert them to `decimal.Decimal`, `bool`, and `datetime.time` values, respectively.

Python's default `TIMESTAMP` converter [ignores UTC offsets](https://bugs.python.org/issue45335) in the database row and always returns a [naive](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects) datetime object. If your `TIMESTAMP` rows contain UTC offsets, you can register your own converter to return aware datetime objects:[^fromisoformat]

```python
import datetime
import sqlite3

sqlite3.register_converter("TIMESTAMP", datetime.datetime.fromisoformat)
```

Keep in mind that it is [generally considered](https://stackoverflow.com/a/33465436/) better practice to store time zone information as a string identifier from the [IANA time zone database](https://www.iana.org/time-zones) in a separate column, rather than use UTC offsets, which change often (e.g., due to daylight saving time).

Adapters and converters are registered globally, not per-database. Be warned that some Python libraries, like Django, [register their own adapters and converters](https://github.com/django/django/blob/stable/3.2.x/django/db/backends/sqlite3/base.py#L75-L80) which will apply even if you use the raw `sqlite3` interface instead of, e.g., Django's ORM.


## Beware of column affinity
<div class="edit">
  Edit (June 2024): As of version 3.37.0, SQLite supports opt-in <a href="https://www.sqlite.org/stricttables.html">STRICT tables</a> which prevent the issues in this section..
</div>

SQLite lets you declare columns with any type that you want (or none at all). This can work nicely with Python's converters and adapters; for example, in one of my projects, I had columns of type `CSV` and used a converter and an adapter to transparently convert them to Python lists and back.

Although SQLite is flexible with typing, ultimately it must choose a [storage class](https://sqlite.org/datatype3.html#storage_classes_and_datatypes) for data, either `TEXT`, `NUMERIC`, `INTEGER`, `REAL`, or `BLOB`. Columns have a "type affinity" which determines the preferred storage class for a column through a [somewhat arbitrary set of rules](https://sqlite.org/datatype3.html#determination_of_column_affinity). This ensures that inserting a string into an `INT` column will convert the string to an integer, for compatibility with other, rigidly-typed database engines.

A corollary of SQLite's flexible typing is that [different values in the same column can have different type affinities](https://www.sqlite.org/datatype3.html):

> In SQLite, the datatype of a value is associated with the value itself, not with its container.

This can cause problems. I once wanted to copy some rows from one table to another. My rows had `TIMESTAMP` columns, and since, as we saw, Python will silently drop UTC offsets, I replaced Python's `TIMESTAMP` converter with one that simply returns the bytes object unchanged:

```python
sqlite3.register_converter("TIMESTAMP", lambda b: b)
```

Unfortunately, this converter resulted in the new `TIMESTAMP` columns having `BLOB` affinity instead of `TEXT`. This was a problem, because some SQL operations are sensitive to the affinities of their operands. One of them is `LIKE`, which does not work on blob values:

```sql
sqlite> SELECT 'a' LIKE 'a';
1
sqlite> SELECT X'61';  -- 0x61 is the hexadecimal value of ASCII 'a'
a
sqlite> SELECT X'61' LIKE 'a';
0
```

Consequently, the query `SELECT * FROM table WHERE date LIKE '2019%'` did not return any of the inserted rows because they all had `BLOB` affinity and the `LIKE` comparison always failed. Only when I ran `SELECT typeof(date) FROM table` did I discover that some of the values in the same column had different affinities.

The correct procedure would have been to register the converter as `lambda b: b.decode()` so that Python would insert string values with `TEXT` affinity.[^why-converters]


## Conclusion
Because I use SQLite in Python so often, I wrote my own library, [isqlite](https://github.com/iafisher/isqlite), that handles most of these issues for me, and also provides a more convenient Python API and many other useful features. You can read about isqlite in [next week's blog post](https://iafisher.com/blog/2021/10/isqlite).


[^dml]: The `sqlite3` docs [use the term](https://docs.python.org/3.8/library/sqlite3.html#controlling-transactions) "Data Modification Language", but it appears that "data manipulation language" is the [standard term](https://en.wikipedia.org/wiki/Data_manipulation_language).
[^fromisoformat]: `datetime.fromisoformat` was added in Python 3.7, so if you are using an older version of Python you will have to write the converter function yourself. You can take a look at how the `sqlite3` module implements the [naive datetime converter](https://github.com/python/cpython/blob/3.8/Lib/sqlite3/dbapi2.py#L66), and adapt it to also read the UTC offset if present. Or you can copy the implementation of [`datetime.fromisoformat`](https://github.com/python/cpython/blob/3.8/Lib/datetime.py#L1717).
[^why-converters]: You might reasonably wonder why I had enabled converters in the first place if I knew that they were not going to work for my `TIMESTAMP` columns. In this case, I was using a library that wrapped `sqlite3.connect` and enabled converters for me.

