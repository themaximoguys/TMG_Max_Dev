# =============================================================================
# Script Information
# =============================================================================
# Script Name: TMG_UTILS
# Type: Library Module (no launch points)
# Active: True
#
# =============================================================================
# Description:
# =============================================================================
# Shared utility functions used across TMG automation scripts. Imported as
# a library; this module is deployed to Maximo as an autoscript with no
# launch points and called from other scripts via:
#
#     from tmg_utils import close_safely, get_string_safe, get_int_safe
#
# Functions follow Jython 2.7 syntax and Maximo coding constraints:
#   - Always close MboSet objects.
#   - Never swallow exceptions.
#   - Use SqlFormat for any user-supplied values in SQL.
#
# =============================================================================
# Imports
# =============================================================================
from psdi.mbo import SqlFormat
from psdi.util.logging import MXLoggerFactory


_LOGGER = MXLoggerFactory.getLogger("maximo.script.tmg_utils")


# =============================================================================
# MboSet handling
# =============================================================================
def close_safely(mbo_set):
    """Close an MboSet, swallowing only the close-time error to keep
    the original exception intact. Use in finally blocks."""
    if mbo_set is None:
        return
    try:
        mbo_set.close()
    except Exception as ce:                                # noqa: E722  (Jython 2.7 syntax)
        _LOGGER.warn("close_safely: error closing MboSet: %s" % str(ce))


# =============================================================================
# Safe field accessors
# =============================================================================
def get_string_safe(mbo, field_name, default=""):
    """Return mbo.getString(field_name) or default if null/empty."""
    if mbo is None:
        return default
    try:
        if mbo.isNull(field_name):
            return default
        value = mbo.getString(field_name)
        if value is None:
            return default
        return value
    except Exception:
        return default


def get_int_safe(mbo, field_name, default=0):
    """Return mbo.getInt(field_name) or default if null."""
    if mbo is None:
        return default
    try:
        if mbo.isNull(field_name):
            return default
        return mbo.getInt(field_name)
    except Exception:
        return default


def get_double_safe(mbo, field_name, default=0.0):
    """Return mbo.getDouble(field_name) or default if null."""
    if mbo is None:
        return default
    try:
        if mbo.isNull(field_name):
            return default
        return mbo.getDouble(field_name)
    except Exception:
        return default


def get_bool_safe(mbo, field_name, default=False):
    """Return mbo.getBoolean(field_name) or default if null."""
    if mbo is None:
        return default
    try:
        if mbo.isNull(field_name):
            return default
        return bool(mbo.getBoolean(field_name))
    except Exception:
        return default


# =============================================================================
# Lookup helpers
# =============================================================================
def fetch_first(mbo, relationship_or_object, where_clause=None, where_params=None):
    """Fetch the first MBO from a relationship or a fresh MboSet.

    If `relationship_or_object` matches a relationship on `mbo`, that path is
    used. Otherwise a top-level MboSet is opened. Caller does NOT need to
    close the returned reference, but must not retain it past commit/rollback.

    `where_params` is a dict; values are bound via SqlFormat to prevent
    SQL injection.
    """
    if mbo is None:
        return None
    mbo_set = None
    try:
        try:
            mbo_set = mbo.getMboSet(relationship_or_object)
        except Exception:
            mxs = mbo.getMboServer() if hasattr(mbo, "getMboServer") else None
            if mxs is None:
                return None
            mbo_set = mxs.getMboSet(relationship_or_object, mbo.getUserInfo())

        if where_clause:
            sf = SqlFormat(mbo, where_clause)
            if where_params:
                for key, val in where_params.iteritems():
                    sf.setObject(key, val)
            mbo_set.setWhere(sf.format())

        first = mbo_set.getMbo(0)
        return first
    finally:
        # Caller may still need the row; mboset close is left to the parent
        # that opened it (Maximo will reap on transaction end). For one-shot
        # reads, callers should call close_safely(...) on the parent.
        pass


def count_where(mbo, object_name, where_clause, where_params=None):
    """Count MBOs in `object_name` matching the SqlFormat-bound clause."""
    if mbo is None:
        return 0
    mxs = mbo.getMboServer() if hasattr(mbo, "getMboServer") else None
    if mxs is None:
        return 0
    mbo_set = None
    try:
        mbo_set = mxs.getMboSet(object_name, mbo.getUserInfo())
        sf = SqlFormat(mbo, where_clause)
        if where_params:
            for key, val in where_params.iteritems():
                sf.setObject(key, val)
        mbo_set.setWhere(sf.format())
        return mbo_set.count()
    finally:
        close_safely(mbo_set)


# =============================================================================
# Validation helpers
# =============================================================================
def is_blank(value):
    """True if the value is None or whitespace-only string."""
    if value is None:
        return True
    try:
        return len(value.strip()) == 0
    except AttributeError:
        return False


def matches_pattern(value, regex_pattern):
    """True if string matches a Java regex (uses java.util.regex)."""
    if value is None:
        return False
    from java.util.regex import Pattern
    return Pattern.compile(regex_pattern).matcher(value).matches()


# =============================================================================
# Logging helper (optional convenience)
# =============================================================================
def log_info(message):
    _LOGGER.info(str(message))


def log_warn(message):
    _LOGGER.warn(str(message))


def log_error(message):
    _LOGGER.error(str(message))


# =============================================================================
# Script Configuration
# =============================================================================
scriptConfig = {
    "autoscript": "TMG_UTILS",
    "description": "Shared utility library used by other TMG automation scripts.",
    "version": "1.0.0",
    "active": True,
    "logLevel": "INFO",
    "scriptLaunchPoints": []
}
