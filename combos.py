# Yes, this file exists for this and this alone. :P

COMBO_FILE = 'combos.txt'

def _read_combos():
  f = open(COMBO_FILE)
  combos = [c.strip() for c in f.readlines() if c.strip()]
  combos.sort()
  return combos

VALID_COMBOS = _read_combos()
