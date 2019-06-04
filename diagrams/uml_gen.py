import codecs
import sadisplay
from donate import models


desc = sadisplay.describe(
    [getattr(models, attr) for attr in dir(models)],
    show_methods=True,
    show_properties=True,
    show_indexes=True,
)

with codecs.open('schema.dot', 'w', encoding='utf-8') as f:
    f.write(sadisplay.dot(desc))
