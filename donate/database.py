import sadisplay
from donate import models
from sqlalchemy.orm import relationship
from .extensions import db
from collections import defaultdict


''' Just a stub right now '''
Column = db.Column
Model = db.Model


def count_levels(name, deps):
    if deps[name] == set():
        return 0
    else:
        return 1 + sum([count_levels(_name, deps) for _name in deps[name]])


def make_dependencies():
    model = sadisplay.describe([getattr(models, attr) for attr in dir(models)])
    tables = model[0]
    relations = model[1]

    names = [table['name'] for table in tables]
    dep_tree = {}

    for name in names:
        dep_tree[name] = set()
        for rel in relations:
            if name == rel['from']:
                dep_tree[name] ^= {rel['to']}

    return dep_tree


def count_dependencies(dep_tree):
    names = dep_tree.keys()
    return {name: count_levels(name, dep_tree) for name in names}
