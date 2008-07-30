import MySQLdb
import loaddb
import time

import logging
from logging import debug, info, warn, error

logging.basicConfig(level=logging.DEBUG)

# Can run as a daemon and tail a number of logfiles and milestones and
# update the db.

class Logfile:
  def __init__(self, filename):
    self.filename = filename
    self.handle = None
    self.offset = None
    self._open()

  def _open(self):
    try:
      self.handle = open(self.filename)
    except:
      warn("Cannot open %s" % self.filename)
      pass

  def have_handle(self):
    if self.handle:
      return True
    self._open()
    return self.handle

  def append(self, cursor):
    if not self.have_handle():
      return

    if not self.offset:
      loaddb.logfile_seek(self.filename, self.handle,
                          loaddb.logfile_offset(cursor, self.filename))

    self.offset = loaddb.tail_file_into_games(cursor, self.filename,
                                              self.handle, self.offset)

def tail_logfiles(logs, interval=3):
  files = [ Logfile(x) for x in logs ]

  db = loaddb.connect_db()
  cursor = db.cursor()
  try:
    while True:
      for logfile in files:
        print "Checking " + logfile.filename
        logfile.append(cursor)
      if not interval:
        break
      print "Sleeping..."
      time.sleep(interval)
  finally:
    cursor.close()
    db.close()

if __name__ == '__main__':
  tail_logfiles( loaddb.LOGS )
