#! /usr/bin/env python

import loaddb
import update_page

print("Hello from update_index")

args = loaddb.load_args()

print("Connecting to database")
db = loaddb.connect_db(host=args.db_host, password=args.db_pass, retry=args.db_retry_connect)

c = db.cursor()
loaddb.support_mysql57(c)
print("Building index page")
try:
  update_page.index_page(c)
finally:
  db.close()
print("All done")
