#! /usr/bin/python
#
# Picks a random combo that has not been won on cao and sets it as Nemelex'
# favoured combo.
#
# Some caveats:
# - The combo should be remembered permanently for future runs of the
#   script with a clean db.
# - The combo should not be won at the point it's chosen.
# - The admin should have the option to reject a combo.
# - The exact instant of activation should be recorded in the text file.
# - The DB will probably have to be dumped after a combo is inserted to
#   make sure no wins get missed.

import MySQLdb
import crawl_utils
import random
import sys
import html
import os.path
from datetime import datetime, timedelta
import time
from loaddb import query_first

NOMINEE_FILE = 'nemelex-combos.txt'
COMBO_VALIDITY_MINIMUM_DAYS = 10
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
REMOTE_COMBO_URL = "http://churnbox.com/nemelex-choice-out.txt"

g_henzell_db = None

def bail(message):
  print
  print '-------------------------------------'
  print message
  print '-------------------------------------'
  sys.exit(1)

def parse_time(when):
  return datetime(*(time.strptime(when, DATE_FORMAT)[0:6]))

def find_previous_nominees(targetfile = NOMINEE_FILE):
  if os.path.exists(targetfile):
    f = open(targetfile)
    nominees = [x.strip().split() for x in f.readlines()
                if x.strip() and not x.strip().startswith('#')]
    f.close()
    return [{'combo': x[0],
             'time': parse_time(x[1] + ' ' + x[2])}
            for x in nominees]
  return []

def assert_validity(pcombo):
  if not pcombo:
    return
  last = pcombo[-1]
  # Don't check validity period.
  if True:
    return
  if (last and ((datetime.utcnow() - last['time']).days
                  < COMBO_VALIDITY_MINIMUM_DAYS)):
    bail(
      ("Combo %s chosen on %s is still valid; " +
       "it will expire only on %s")
      % (last['combo'], html.pretty_date(last['time']),
         html.pretty_date(last['time']
                          + timedelta(COMBO_VALIDITY_MINIMUM_DAYS))))

def apply_combo(combo, tofile = NOMINEE_FILE):
  time = datetime.utcnow()
  validity = time + timedelta(COMBO_VALIDITY_MINIMUM_DAYS)
  f = open(tofile, 'a')
  f.write("%s %s\n" % (combo, time.strftime(DATE_FORMAT)))
  f.close()
  print(("OK, %s is now the official Nemelex Choice, " +
         "valid at least until %s")
        % (combo, html.pretty_date(validity)))

def filter_combos(combos, filters):
  race_set = set([x[:2] for x in filters])
  class_set = set([x[2:] for x in filters])
  return [x for x in combos if x[:2] not in race_set and x[2:] not in class_set]

def stop_taildb_and_lock():
  taildb_running = False
  while True:
    try:
      crawl_utils.lock_or_throw()
      return taildb_running
    except IOError:
      if not taildb_running:
        crawl_utils.write_taildb_stop_request()
        print "taildb.py appears to be running, requesting it to stop."
      taildb_running = True
    print "Waiting..."
    time.sleep(2)

def restart_taildb():
  if not os.path.exists('taildb.py'):
    raise Exception("Cannot find taildb.py script!")
  print "Restarting taildb.py"
  os.system('python taildb.py')

def fetch_combo_from_remote():
  old_size = os.path.getsize(NOMINEE_FILE)
  while old_size == os.path.getsize(NOMINEE_FILE):
    os.system('wget -c %s -O %s' % (REMOTE_COMBO_URL, NOMINEE_FILE))
    time.sleep(2)

  nominee = find_previous_nominees()[-1]
  print "New nominee: #{nominee['combo']} at #{nominee['time']}"

if __name__ == '__main__':
  try:
    print "Selecting a combo to nominate for Nemelex' Choice"
    taildb_needs_restart = stop_taildb_and_lock()
    fetch_combo_from_remote()
    crawl_utils.clear_taildb_stop_request()
    if taildb_needs_restart:
      crawl_utils.unlock_handle()
      restart_taildb()
  except KeyboardInterrupt:
    print "\nAborted by user."
