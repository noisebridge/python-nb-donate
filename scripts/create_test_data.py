from donate.database import (
    make_dependencies,
    count_dependencies
)
import importlib
import json
from collections import defaultdict


def connect_objects(objects):
    deps = make_dependencies()
    dep_depths = count_dependencies(deps)


def main():
    modile = importlib.import_module('donate.models')
    objects = defaultdict(list)

    with open("../data/test_data.json", 'r') as f:
        data = json.read(f)

    for obj, instances in data.items():
        _class = getattr(mod, obj)
        for instance in instances:
            objects[obj].append(_class(**instance))
