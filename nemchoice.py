#! /usr/bin/python

import nominate_combo
from datetime import datetime

def _fixup_nominee_validity(c):
  newcombos = []
  for i in range(0, len(c)):
    cur = c[i]
    next = None
    if i < len(c) - 1:
      next = c[i + 1]['time']
    newcombos.append([cur['combo'], cur['time'], next])
  return newcombos

NEMELEX_COMBOS = _fixup_nominee_validity(
  nominate_combo.find_previous_nominees())
NEMELEX_SET = set([x[0] for x in NEMELEX_COMBOS])

def _to_date(when):
  if when.endswith('D') or when.endswith('S'):
    when = when[:-1]
  return datetime.strptime(when, '%Y%m%d%H%M%S')

def is_nemelex_choice(combo, when):
  """Returns true if the given combo for a game that ended at the given
  datetime is a chosen combo for the Nemelex' Choice banner."""
  if isinstance(when, str) or isinstance(when, unicode):
    when = _to_date(when)
  if combo in NEMELEX_SET:
    for c in NEMELEX_COMBOS:
      if c[0] == combo and when >= c[1] and (not c[2] or when < c[2]):
        return True
  return False
