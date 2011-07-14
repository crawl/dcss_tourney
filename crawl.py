#! /usr/bin/python

NRUNES = 16

GODS = ['No God', 'Zin', 'The Shining One', 'Kikubaaqudgha',
        'Yredelemnul', 'Xom', 'Vehumet', 'Okawaru', 'Makhleb',
        'Sif Muna', 'Trog', 'Nemelex Xobeh', 'Elyvilon', 'Lugonu',
        'Beogh', 'Fedhas', 'Jiyva', 'Cheibriados', 'Ashenzari']

MAGIC_SKILLS = ['Spellcasting', 'Conjurations', 'Hexes', 'Charms',
                'Summonings', 'Necromancy', 'Translocations',
                'Transmutations', 'Fire Magic', 'Ice Magic',
                'Air Magic', 'Earth Magic', 'Poison Magic']

FRUIT_BITS = { "orange"     : 0x00040,
               "banana"     : 0x00080,
               "lemon"      : 0x00100,
               "pear"       : 0x00200,
               "apple"      : 0x00400,
               "apricot"    : 0x00800,
               "choko"      : 0x01000,
               "rambutan"   : 0x02000,
               "lychee"     : 0x04000,
               "strawberry" : 0x08000,
               "grape"      : 0x10000,
               "sultana"    : 0x20000
             }
FRUITS = sorted(FRUIT_BITS.keys())

def _full_fruit_mask():
  mask = 0
  for fruit in FRUIT_BITS:
    mask = mask | FRUIT_BITS[fruit]
  return mask

FULL_FRUIT_MASK = _full_fruit_mask()

def fruit_basket_complete(fruit_mask):
  return fruit_mask == FULL_FRUIT_MASK

def fruit_mask_to_fruits(fruit_mask):
  fruits = [ ]
  for f in FRUITS:
    if fruit_mask & FRUIT_BITS[f]:
      fruits.append(f)
  return fruits
