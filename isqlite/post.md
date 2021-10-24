# isqlite: An improved Python interface to SQLite
In [last week's post](https://iafisher.com/blog/2021/10/using-sqlite-effectively-in-python), I wrote about how to use SQLite effectively in Python. Since I use SQLite and Python in many of my personal projects, I wrote my own library that wraps Python's `sqlite3` module with a better API, support for schema migrations like in [Django](https://docs.djangoproject.com/en/3.2/topics/migrations/), and a command-line interface. I call it isqlite.


## Better Python API
Python's standard `sqlite3` module was designed to be compliant with the DB-API 2.0 standard described in [PEP 249](https://www.python.org/dev/peps/pep-0249/). DB-API 2.0 is conservative in the operations it requires modules to implement. In particular, the API provides no help in constructing specific SQL statements, instead only exposing `execute` and `executemany` methods and requiring the library user to write all the SQL themselves.

I find SQL syntax difficult to remember, especially since `SELECT`, `INSERT`, `UPDATE`, and `DELETE` queries are all structured differently, so isqlite provides methods for common SQL operations:

```python3
with Database(":memory:") as db:
    # Create a new employee.
    db.insert("employees", {"name": "John Doe", "title": "Software Engineer"})
    
    # Fetch all managers.
    managers = db.select("employees", where="title = 'Manager'")
    # Return value is a list of OrderedDict objects.
    print(managers[0]["name"])
    
    # Set a holiday bonus for all employees with a certain tenure.
    db.update(
      "employees",
      {"holiday_bonus": 500},
      where="tenure >= :tenure",
      values={"tenure": MINIMUM_TENURE_FOR_BONUS},
    )
```

Instead of requiring you to call `fetchone` or `fetchall` to get the results of your queries, isqlite returns the rows directly, as [`OrderedDict`](https://docs.python.org/3/library/collections.html#collections.OrderedDict) objects instead of tuples to make them easier to use.

isqlite also has helper methods for common patterns (`get_by_pk`, `insert_and_get`, `get_or_insert`) and can automatically and efficiently fetch related rows using the `get_related` parameter:

```python
book = db.get_by_pk("books", 123, get_related=["author"])
# Full author row has been fetched and embedded in the book object.
print(book["author"]["name"])
```

If you need to drop into raw SQL, you can easily do so with the `Database.sql` method, which is a thin wrapper around `sqlite3.execute`.


## Schema migrations
Where isqlite really shines is in its support for schema migrations. isqlite can take a schema written in Python, e.g.

```python
from isqlite import Schema, Table, columns

SCHEMA = Schema(
  [
    Table(
      "authors",
      [
        columns.text("first_name"),
        columns.text("last_name"),
        columns.text("country", required=False),
      ],
    ),
    Table(
      "books",
      [
        columns.text("title"),
        columns.foreign_key("author", foreign_table="authors"),
      ],
    ),
  ]
)
```

...diff the Python schema against the actual database schema, and run the SQL commands to make the two match. Migrating your database to a new schema is as easy as running `isqlite migrate path/to/db path/to/schema.py` and confirming the list of changes to be made. isqlite is able to detect renaming of columns and tables and reordering of columns within a table as well as adding and dropping columns.

There are a few reasons to write the schema in Python:

- Schema changes can be tracked by version control.
- An explicit schema ensures that all deployments of the applications are using the same database schema.
- Common patterns can be simplified with Python code, e.g. isqlite provides an `AutoTable` class that automatically creates a primary key column called `id` and `created_at` and `last_updated_at` timestamp columns. The `text_column` macro enforces that all `TEXT` columns must be non-null so that there is only one way to represent the absence of a value (the empty string).

If you prefer, you can manually make schema alterations on the command-line with commands like `isqlite add-column` and `isqlite drop-table`. This does not require a Python schema.


## Odds and ends
As mentioned in [my previous post on SQLite](https://iafisher.com/blog/2021/10/using-sqlite-effectively-in-python), SQLite disables foreign-key constraint enforcement by default. isqlite turns it back on.

isqlite handles SQL transactions in a straightforward manner. If you connect to the database in a `with` statement, a transaction is automatically opened and persists for the length of the `with` statement. The transaction will be committed at the end or rolled back if an exception occurred.

If you need more finely-grained control of transactions, you can use `Database.transaction` as a context manager:

```python
with Database(":memory:", transaction=False) as db:
    with db.transaction():
        ...

    with db.transaction():
        ...
```

isqlite turns on [converters](https://docs.python.org/3/library/sqlite3.html#converting-sqlite-values-to-custom-python-types) so that SQL values are mapped to corresponding Python values where possible, and registers a few useful converters and adapters of its own for `datetime.time` and `decimal.Decimal` values.


## Uses
isqlite is designed as a replacement for the built-in `sqlite3` module, not for a full-fledged ORM like [SQLAlchemy](https://www.sqlalchemy.org/). isqlite does not and will never support any database engine other than SQLite, which makes it less than suitable for, e.g., a realistic web application. However, it is a good fit for applications that [use SQLite as a file format](https://sqlite.org/appfileformat.html), for hobby projects that will never need a client-server database engine like Postgres, and for *ad hoc* database operations on the command-line.

If you'd like to try isqlite out for yourself, you can install it with pip:

```shell
$ pip3 install isqlite
```

Comprehensive documentation is available online at <https://isqlite.readthedocs.io/en/latest/>, and bug reports and feature requests can be filed at <https://github.com/iafisher/isqlite/issues>.
