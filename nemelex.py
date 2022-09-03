#! /usr/bin/python

import MySQLdb
import crawl_utils
import random
import sys
import os.path
from datetime import datetime
import time
import query
import combos
from loaddb import START_TIME, LOG_DB_MAPPINGS, make_xlog_db_query, query_first

import logging
from logging import debug, info, warn, error

NOMINEE_FILE = 'nemelex-combos.txt'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

NEMELEX_USE_LIST = True

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

def weight_combos(combos, previous):
  weights = []
  for x in combos:
    w = 1
    for y in previous:
      if x[:2] == y[:2] or x[2:] == y[2:]:
        w *= 10
    weights.append(w)
  return weights

def current_nemelex_choice():
  return NEMELEX_COMBOS and NEMELEX_COMBOS[-1]

def list_nemelex_choices(c):
  # Check the file again so that we don't miss one.
  combos = _fixup_nominee_validity(find_previous_nominees())
  nem_list = []
  for x in combos:
    nem_list.append([x[0], x[1], min(count_nemelex_wins(c,x[0]), 9),
        min(count_clan_nemelex_wins(c,x[0]), 9)])
  return nem_list

def is_nemelex_choice(combo, when):
  """Returns true if the given combo for a game that ended at the given
  datetime is a chosen combo for the Nemelex' Choice banner."""
  if combo in NEMELEX_SET:
    for c in NEMELEX_COMBOS:
      if c[0] == combo:
        return True
  return False

def eligible_combos(c):
  # first one is always picked from the special list
  if len(NEMELEX_COMBOS) == 0:
    return [combos.NEM_ELIGIBLE_COMBOS]
  # sometimes look at the special list for the later ones, too
  if NEMELEX_USE_LIST:
    won_games = query.get_winning_games(c)
    won_combos = set([x['charabbrev'] for x in won_games])
    eligible =  [x for x in combos.NEM_ELIGIBLE_COMBOS
                 if (x not in won_combos)]
    pcombo_names = [x[0] for x in NEMELEX_COMBOS]
    weighting = weight_combos(eligible, pcombo_names)
    return [eligible,weighting]
  # otherwise pick from the valid combos with the lowest high score in the tourney:
  else:
    eligible = combos.VALID_COMBOS
    pcombo_names = [x[0] for x in NEMELEX_COMBOS]
    # Try not to use a repeat race or class if possible.
    filtered_eligible = filter_combos(eligible, pcombo_names)
    if filtered_eligible:
      eligible = filtered_eligible
    eligible_with_scores = [[combo_name, query.highscore(c, combo_name)] for combo_name in eligible]
    eligible_with_scores.sort(key = lambda e: e[1])
    l = 19
    if l > len(eligible_with_scores)-1:
      l = len(eligible_with_scores)-1
    candidates = [e[0] for e in eligible_with_scores if e[1] <= eligible_with_scores[l][1]]
    return [candidates]

def pick_combo(data):
  if data[0]:
    eligible = data[0]
    if len(data) > 1:
      weighting = data[1]
      n = len(eligible)
      combo = None
      while not combo:
        i = random.randrange(len(eligible))
        if random.randrange(weighting[i]) == 0:
          combo = eligible[i]
    else:
      combo = eligible[random.randrange(len(eligible))]
    apply_combo(combo)

def need_new_combo(c):
  if not NEMELEX_COMBOS:
    nowtime = datetime.utcnow().strftime('%Y%m%d%H%M')
    return (nowtime >= START_TIME)
  return (count_nemelex_wins(c, current_nemelex_choice()[0]) > 0)

def award_nemelex_win(c, xdict, filename):
    iq = make_xlog_db_query(LOG_DB_MAPPINGS, xdict, filename, None,
                            'player_nemelex_wins')
    try:
      iq.execute(c)
    except Exception as e:
      error("Error inserting %s into %s (query: %s [%s]): %s"
            % (xdict, 'player_nemelex_wins', iq.query, iq.values, e))
      raise

def player_has_nemelex_win(c, player, char):
    return (query_first(c, '''SELECT COUNT(*) FROM player_nemelex_wins
                              WHERE player = %s AND charabbrev = %s''',
                              player, char) > 0)
 
def count_clan_nemelex_wins(c, char):
    return query_first(c, '''SELECT COUNT(*) FROM clan_nemelex_wins
                             WHERE clan_finish = 1 AND charabbrev = %s''',
                             char)

def count_nemelex_wins(c, char):
    return query_first(c, '''SELECT COUNT(*) FROM player_nemelex_wins
                             WHERE charabbrev = %s''', char)
