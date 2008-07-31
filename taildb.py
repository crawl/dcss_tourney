import MySQLdb
import loaddb
import time
import crawl_utils

import logging
from logging import debug, info, warn, error

import teams

BASEDIR = '/home/crawl'

# Can run as a daemon and tail a number of logfiles and milestones and
# update the db.

class Xlogfile:
  def __init__(self, filename, tell_op, tail_op):
    self.filename = filename
    self.handle = None
    self.offset = None
    self.tell_op = tell_op
    self.tail_op = tail_op
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
      loaddb.xlog_seek(self.filename, self.handle,
                       self.tell_op(cursor, self.filename))

    self.offset = self.tail_op(cursor, self.filename,
                               self.handle, self.offset)

class Logfile (Xlogfile):
  def __init__(self, filename):
    Xlogfile.__init__(self, filename, loaddb.logfile_offset,
                      loaddb.tail_file_into_games)

class MilestoneFile (Xlogfile):
  def __init__(self, filename):
    Xlogfile.__init__(self, filename, loaddb.milestone_offset,
                      loaddb.tail_milestones)

def tail_files(files):
  for logfile in files:
    logfile.append(cursor)

def interval_work(interval, files):
  tail_files(files)
  # Any other stuff can be done here.

def tail_logfiles(logs, milestones, interval=60):
  files = [ MilestoneFile(x) for x in milestones ] + \
      [ Logfile(x) for x in logs ]

  db = loaddb.connect_db()
  loaddb.init_listeners(db)

  cursor = db.cursor()
  try:
    while True:
      interval_work(interval, files)
      if not interval:
        break
      time.sleep(interval)
  finally:
    cursor.close()
    loaddb.cleanup_listeners(db)
    db.close()

if __name__ == '__main__':
  loaddb.load_extensions()

  logging.basicConfig(level=logging.DEBUG,
                      filename = BASEDIR + '/taildb.log')
  crawl_utils.daemonize(BASEDIR + '/taildb.lock')
  tail_logfiles( loaddb.LOGS, loaddb.MILESTONES, 60 )
