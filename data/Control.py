from Smartphones_db import *

with db:
    db.create_tables([Smartphones])

print('done')