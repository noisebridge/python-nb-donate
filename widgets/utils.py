from ..extensions import db


def exists(cls, keys, fuzzy=False):
    ''' finds instance of class cls by using a dictionary of keys.  Will
    match using 'and' by default, but if fuzzy is True, matches with 'or' to
    see if any object matches at least one criterial.
    keys = {cls.attribute: attribute value}
    If the match is fuzzy, then non-exiting attributes are ignored.  If the
    match is exact, then the query will throw an error about the class not
    having the requested property.'''

    if not fuzzy:
        return db.session.query(cls).filter_by(**keys).count() > 0
    else:
        _keys = list(keys.keys())
        _values = list(keys.values())

        clause = (getattr(cls, _keys[0], None) == _values[0])
        for _x in range(1, len(_keys)):
            clause |= (getattr(cls, _keys[_x], None) == _values[_x])

        return db.session.query(cls).fliter_by(clause).count() > 0
