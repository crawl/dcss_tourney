# Yes, this file exists for this and this alone. :P

COMBO_FILE = 'combos.txt'
NEM_ELIGIBLE_FILE = 'nem_eligible.txt'

def _read_combos(filename):
  f = open(filename)
  combos = [c.strip() for c in f.readlines() if c.strip()]
  combos.sort()
  return combos

VALID_COMBOS = _read_combos(COMBO_FILE)
NEM_ELIGIBLE_COMBOS = _read_combos(NEM_ELIGIBLE_FILE)
