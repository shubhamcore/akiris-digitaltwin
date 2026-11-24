"""Reuse read-only SQLite dashboard aggregates while their source is unchanged."""
from collections import OrderedDict

from sqlalchemy.orm import Session


def read_snapshot(db: Session, key: tuple, compute):
    conn = db.connection()
    if conn.dialect.name != "sqlite":
        return compute()
    raw = conn.connection.driver_connection
    if raw.in_transaction or db.new or db.dirty or db.deleted:
        return compute()

    def version():
        # data_version tracks commits by other connections. The other two
        # counters also catch DML and DDL on this same physical connection.
        return conn.exec_driver_sql(
            "SELECT data_version, schema_version, total_changes() "
            "FROM pragma_data_version, pragma_schema_version").one()

    current = version()
    cache = conn.info.setdefault("twinline_reads", OrderedDict())
    if key in cache and cache[key][0] == current:
        cache.move_to_end(key)
        return cache[key][1]
    value = compute()
    if version() == current and not raw.in_transaction:
        cache[key] = current, value
        cache.move_to_end(key)
        if len(cache) > 32:
            cache.popitem(last=False)
    return value

