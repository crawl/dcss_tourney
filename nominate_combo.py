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

import crawl_utils
import random
import sys
import html
import os.path
from datetime import datetime, timedelta

NOMINEE_FILE = 'nemelex-combos.txt'
COMBO_VALIDITY_MINIMUM_DAYS = 10
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

UNWON_FILE = '/home/henzell/henzell/unwon.txt'

EXCLUDED_COMBOS = ['GhPa']

# Skip obsolete and new races
EXCLUDED_RACES = ['GE', 'El', 'HD', 'Gn', 'DD']
EXCLUDED_CLASSES = ['Ar']

def _clean_unwon_lines(lines):
  def extract_character(l):
    char = l.split()[0]
    if len(char) == 4:
      return char

  def dud_char(c):
    return ((c in EXCLUDED_COMBOS)
            or (c[:2] in EXCLUDED_RACES)
            or (c[2:] in EXCLUDED_CLASSES))

  return [c for c in [extract_character(x) for x in lines[1:]]
          if c and not dud_char(c)]

def get_unwon_combos():
  f = open(UNWON_FILE)
  lines = f.readlines()
  f.close()
  return _clean_unwon_lines(lines)

def is_still_unwon(combo):
  return True

def find_random_unwon(all_unwon):
  trials = 0
  while trials < 100:
    combo = all_unwon[random.randrange(len(all_unwon))]
    if is_still_unwon(combo):
      return combo
    trials += 1

def bail(message):
  print
  print '-------------------------------------'
  print message
  print '-------------------------------------'
  sys.exit(1)

def parse_time(when):
  return datetime(*(time.strptime(when, DATE_FORMAT)[0:6]))

def find_previous_nominees():
  if os.path.exists(NOMINEE_FILE):
    f = open(NOMINEE_FILE)
    nominees = [x.strip().split() for x in f.readlines()
                if not x.strip().startswith('#')]
    return [{'combo': x[0],
             'time': parse_time(x[1] + ' ' + x[2])}
            for x in nominees]
  return []

def assert_validity(pcombo):
  if not pcombo:
    return
  last = pcombo[-1]
  if (last and ((datetime.utcnow() - last['time']).days
                  < COMBO_VALIDITY_MINIMUM_DAYS)):
    bail(
      ("Combo %s chosen on %s is still valid; " +
       "it will expire only on %s")
      % (last['combo'], html.pretty_date(last['time']),
         html.pretty_date(last['time']
                          + timedelta(COMBO_VALIDITY_MINIMUM_DAYS))))

def apply_combo(combo):
  time = datetime.utcnow()
  validity = time + timedelta(COMBO_VALIDITY_MINIMUM_DAYS)
  f = open(NOMINEE_FILE, 'a')
  f.write("%s %s\n" % (combo, time.strftime(DATE_FORMAT)))
  f.close()
  print(("OK, %s is now the official Nemelex Choice, " +
         "valid at least until %s")
        % (combo, html.pretty_date(validity)))

def pick_unwon_combo():
  pcombo = find_previous_nominees()
  assert_validity(pcombo)
  pcombo_names = [x[0] for x in pcombo]

  all_unwon = get_unwon_combos()

  def is_real_combo(combo, existing_combos):
    return combo in all_unwon

  def is_dupe(combo, pcombo_names):
    return combo in pcombo_names

  while True:
    chosen = find_random_unwon(all_unwon)
    if not chosen:
      raise Exception("Failed to choose a random unwon combo!")
    print("\n---> %s as the next Nemelex' Choice? (effective immediately)"
          % chosen)
    print "Hit Enter to continue, or enter an alternative combo, or ^C to cancel"
    combo = sys.stdin.readline().strip()
    if combo:
      if not is_real_combo(combo, all_unwon):
        print(combo + " is not a valid combo. You may use one of " +
              ", ".join(all_unwon))
        continue
      if not is_still_unwon(combo):
        print(combo + " has been won, sorry!")
        all_unwon = [x for x in all_unwon if x != combo]
        continue
      if is_dupe(combo, pcombo_names):
        print(combo + " has already been used.")
        continue
      return apply_combo(combo)
    return apply_combo(chosen)

if __name__ == '__main__':
  try:
    print "Selecting a combo to nominate for Nemelex' Choice"
    print "Please kill taildb.py if it's running and restart after we're done here."
    crawl_utils.lock_or_die()
    random.seed()
    pick_unwon_combo()
  except KeyboardInterrupt:
    print "\nAborted by user."
