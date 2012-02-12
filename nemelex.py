#! /usr/bin/python

import MySQLdb
import crawl_utils
import random
import sys
import html
import os.path
from datetime import datetime
import time
import query
import combos
from banner import count_recipients
from loaddb import START_TIME

NOMINEE_FILE = 'nemelex-combos.txt'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

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

def _fixup_nominee_validity(c):
  newcombos = []
  for i in range(0, len(c)):
    cur = c[i]
    next = None
    if i < len(c) - 1:
      next = c[i + 1]['time']
    newcombos.append([cur['combo'], cur['time'], next])
  return newcombos

NEMELEX_COMBOS = _fixup_nominee_validity(find_previous_nominees())
NEMELEX_SET = set([x[0] for x in NEMELEX_COMBOS])

def apply_combo(combo, tofile = NOMINEE_FILE):
  time = datetime.utcnow()
  f = open(tofile, 'a')
  f.write("%s %s\n" % (combo, time.strftime(DATE_FORMAT)))
  f.close()
  global NEMELEX_COMBOS
  global NEMELEX_SET
  NEMELEX_COMBOS = _fixup_nominee_validity(find_previous_nominees())
  NEMELEX_SET = set([x[0] for x in NEMELEX_COMBOS])

def filter_combos(combos, filters):
  race_set = set([x[:2] for x in filters])
  class_set = set([x[2:] for x in filters])
  return [x for x in combos if x[:2] not in race_set and x[2:] not in class_set]

def current_nemelex_choice():
  return NEMELEX_COMBOS and NEMELEX_COMBOS[-1]

def list_nemelex_choices(c):
  # Check the file again so that we don't miss one.
  combos = _fixup_nominee_validity(find_previous_nominees())
  nem_list = []
  for x in combos:
    ban = 'nemelex:' + x[0]
    nem_list.append([x[0], x[1], count_recipients(c, ban, 3)])
  return nem_list

def is_nemelex_choice(combo, when):
  """Returns true if the given combo for a game that ended at the given
  datetime is a chosen combo for the Nemelex' Choice banner."""
  if combo in NEMELEX_SET:
    if isinstance(when, str) or isinstance(when, unicode):
      when = query.time_from_str(when)
    for c in NEMELEX_COMBOS:
      if c[0] == combo:
        return True
  return False

def eligible_combos(c):
  won_games = query.get_winning_games(c)
  won_combos = set([x['charabbrev'] for x in won_games])
  return [x for x in combos.NEM_ELIGIBLE_COMBOS
          if (x not in won_combos)]

def pick_combo(eligible):
  if eligible:
    pcombo_names = [x[0] for x in NEMELEX_COMBOS]
    # Try not to force a repeat race or class if possible.
    filtered_eligible = filter_combos(eligible, pcombo_names)
    if filtered_eligible:
      eligible = filtered_eligible
    combo = eligible[random.randrange(len(eligible))]
    apply_combo(combo)

def need_new_combo(c):
  if not NEMELEX_COMBOS:
    nowtime = datetime.utcnow().strftime('%Y%m%d')
    return (nowtime >= START_TIME)
  ban = 'nemelex:' + current_nemelex_choice()[0]
  return (count_recipients(c, ban, 3) > 0)
