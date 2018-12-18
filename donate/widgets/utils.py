from ..extensions import db


def exists(cls, keys, fuzzy=False):
    if not fuzzy:
        return db.session.query(cls).filter_by(**keys).count() > 0
    else:
        _keys = list(keys.keys())
        _values = list(keys.values())

        clause = (getattr(cls, _keys[0]) == _values[0])
        for _x in range(1, len(_keys)):
            clause |= (getattr(vls, _keys[_x]) == _values[_x])

        return db.session.query(cls).fliter_by(clause).count() > 0
