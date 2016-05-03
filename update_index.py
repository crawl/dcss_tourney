#! /usr/bin/env python

import loaddb
import update_page

db = loaddb.connect_db()
c = db.cursor()
loaddb.support_mysql57(c)
try:
  update_page.index_page(c)
finally:
  db.close()
