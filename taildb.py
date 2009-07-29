import MySQLdb
import loaddb
import time
import crawl_utils

import logging
from logging import debug, info, warn, error

# Can run as a daemon and tail a number of logfiles and milestones and
# update the db.
def interval_work(cursor, interval, master):
  master.tail_all(cursor)

def tail_logfiles(logs, milestones, interval=60):
  db = loaddb.connect_db()
  loaddb.init_listeners(db)

  cursor = db.cursor()
  elapsed_time = 0

  master = loaddb.create_master_reader()
  try:
    while True:
      try:
        interval_work(cursor, interval, master)
        if not interval:
          break
        loaddb.run_timers(cursor, elapsed_time)
      except IOError, e:
        error("IOError: %s" % e)

      time.sleep(interval)
      elapsed_time += interval
  finally:
    cursor.close()
    loaddb.cleanup_listeners(db)
    db.close()

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG,
                      filename = (crawl_utils.BASEDIR + '/taildb.log'))
  loaddb.load_extensions()
  crawl_utils.daemonize()
  tail_logfiles( loaddb.LOGS, loaddb.MILESTONES, 130 )
