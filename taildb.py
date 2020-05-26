import MySQLdb
import loaddb
import time
import crawl_utils
import sys

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
  loaddb.support_mysql57(cursor)
  loaddb.set_active_cursor(cursor)
  elapsed_time = 0

  master = loaddb.create_master_reader()
  try:
    while True:
      try:
        interval_work(cursor, interval, master)
        if not interval:
          break
        loaddb.run_timers(cursor, elapsed_time)
      except IOError as e:
        error("IOError: %s" % e)

      time.sleep(interval)
      elapsed_time += interval

      if crawl_utils.taildb_stop_requested():
        info("Exit due to taildb stop request.")
        break
  finally:
    loaddb.set_active_cursor(None)
    cursor.close()
    loaddb.cleanup_listeners(db)
    db.close()

if __name__ == '__main__':
  if crawl_utils.taildb_stop_requested():
    print("""The taildb sentinel %s exists. The Nemelex' Choice script may be active."""
          % crawl_utils.TAILDB_STOP_REQUEST_FILE)
    print ("""If you're sure it is not, please remove the file and restart taildb.py""")
    sys.exit(1)
  logging.basicConfig(level=logging.DEBUG,
                      format=crawl_utils.LOGFORMAT,
                      filename = (crawl_utils.BASEDIR + '/taildb.log'))
  loaddb.load_extensions()
  crawl_utils.daemonize()
  tail_logfiles( loaddb.LOGS, loaddb.MILESTONES, 30 )
