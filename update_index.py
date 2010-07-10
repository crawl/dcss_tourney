#! /usr/bin/env python

import loaddb
import update_page

db = loaddb.connect_db()
try:
  update_page.index_page(db.cursor())
finally:
  db.close()
