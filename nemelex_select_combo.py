#! /usr/bin/python
#
# Selects a combo for Nemelex' Choice.

import MySQLdb
import combos
import sys
import random
from loaddb import query_rows, query_first
from nominate_combo import assert_validity, apply_combo, parse_time
from nominate_combo import find_previous_nominees, filter_combos

DB = MySQLdb.connect(host = 'localhost',
                     user = 'henzell',
                     db = 'henzell')

TARGETFILE = 'nemelex-choice-out.txt'

AUTOMATIC = __name__ == '__main__' and [x for x in sys.argv if x == '--auto']

MAX_WINS = 1

def eligible_combos(c):
  # Pick low-winning combos, excluding the species that are either too
  # cheap or encourage scumming.
  unusable = query_rows(c,
                        """SELECT charabbrev, COUNT(*) AS wins FROM logrecord
                            WHERE killer = 'winning' AND cv >= '0.4'
                         GROUP BY charabbrev
                           HAVING wins > %d""" % MAX_WINS)
  unusable_combos = set([x[0] for x in unusable])
  return [x for x in combos.VALID_COMBOS
          if (x not in unusable_combos
              and not x[:2] in ['DD', 'Mu', 'DE', 'HE', 'Sp', 'Ce']
              and not x[2:] in ['AM', 'Ar'])]

def _connect_henzell_db():
  db = MySQLdb.connect(host='localhost',
                       user='henzell',
                       db='henzell')
  return db

def with_henzell_cursor(action):
  cursor = DB.cursor()
  res = None
  try:
    res = action(cursor)
  finally:
    cursor.close()
  return res

def is_still_unwon(combo):
  def is_combo_unwon(c):
    q = query_first(c,
                    '''SELECT COUNT(*) FROM logrecord
                       WHERE charabbrev = %s AND ktyp = 'winning' AND cv >= '0.4' ''',
                    combo)
    return q <= MAX_WINS
  return with_henzell_cursor(is_combo_unwon)

def find_random_unwon(all_unwon):
  trials = 0
  while trials < 100:
    combo = all_unwon[random.randrange(len(all_unwon))]
    if is_still_unwon(combo):
      return combo
    trials += 1

def pick_combo(all_unwon):
  pcombo = find_previous_nominees(TARGETFILE)
  assert_validity(pcombo)
  pcombo_names = [x['combo'] for x in pcombo]

  # Try not to force a repeat race or class if possible.
  filtered_unwon = filter_combos(all_unwon, pcombo_names)
  if filtered_unwon:
    all_unwon = filtered_unwon

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
    combo = None
    if not AUTOMATIC:
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
      return apply_combo(combo, TARGETFILE)
    return apply_combo(chosen, TARGETFILE)

def main():
  c = DB.cursor()
  try:
    random.seed()
    combos = eligible_combos(c)
    pick_combo(combos)
  finally:
    c.close()

if __name__ == '__main__':
  main()
