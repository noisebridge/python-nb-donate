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
    module = importlib.import_module('donate.models')
    objects = defaultdict(list)
    deps = make_dependencies()
    dep_counts = count_dependencies()

    with open("./data/test_data.json", 'r') as f:
        data = json.load(f)

    for obj, instances in data.items():
        _class = getattr(module, obj)
        for instance in instances:
            objects[obj].append(_class(**instance))

    for class_name in objects.keys():
        obj = objects[class_name]
        obj_deps = deps[class_name]
        # now that you have deps, how do you attach dep to object without
        # predetermining the object field?
    return objects
