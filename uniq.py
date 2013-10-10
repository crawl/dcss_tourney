UNIQUES = [ "Ijyb", "Blork", "Urug", "Erolcha", "Snorg",
            "Antaeus", "Xtahua", "Tiamat", "Boris", "Murray", "Terence",
            "Jessica", "Sigmund", "Edmund", "Psyche", "Donald",
            "Joseph", "Erica", "Josephine", "Harold",
            "Agnes", "Maud", "Louise", "Frances", "Rupert", "Wiglaf",
            "Norris", "Frederick", "Margery", "Mnoleg", "Lom Lobon",
            "Cerebov", "Gloorx Vloq", "Geryon", "Dispater", "Asmodeus",
            "Ereshkigal", "Nessos", "Azrael", "Polyphemus",
            "Prince Ribbit", "the royal jelly", "Dissolution", "Sonja",
            "Nergalle", "Saint Roka", "Roxanne", "Eustachio",
            "the Lernaean hydra", "Dowan", "Duvessa",
            "Grum", "Crazy Yiuf", "Gastronok", "Pikel", "Menkaure",
            "Khufu", "Ilsuiw", "Aizul", "Mara", "Purgy", "Grinder",
            "Kirke", "Nikola", "Maurice", "Mennas", "Jory", 
            "the Serpent of Hell", "the Enchantress", "Ignacio", "Arachne", "Fannar", "Jorgrun", "Lamia", "Sojobo" ]

HARD_UNIQUES = [ "Antaeus", "Asmodeus", "Boris", "Cerebov", "Dispater", "Dissolution", "Ereshkigal", "Frederick", "Geryon", "Gloorx Vloq", "Ignacio", "Ilsuiw", "Jory", "Khufu", "Lom Lobon", "Mara", "Margery", "Mennas", "Mnoleg", "Murray", "Sojobo", "the Enchantress", "the Lernaean hydra", "the Serpent of Hell", "the royal jelly", "Tiamat", "Xtahua" ]

MEDIUM_UNIQUES = [ "Agnes", "Aizul", "Arachne", "Azrael", "Donald", "Frances", "Jorgrun", "Kirke", "Lamia", "Louise", "Maud", "Nergalle", "Nessos", "Nikola", "Norris", "Polyphemus", "Roxanne", "Rupert", "Saint Roka", "Snorg", "Wiglaf" ]

EASY_UNIQUES = [ "Blork", "Crazy Yiuf", "Dowan", "Duvessa", "Edmund", "Erica", "Erolcha", "Eustachio", "Fannar", "Gastronok", "Grum", "Grinder", "Harold", "Ijyb", "Jessica", "Joseph", "Josephine", "Maurice", "Menkaure", "Pikel", "Prince Ribbit", "Psyche", "Purgy", "Sigmund", "Sonja", "Terence", "Urug" ]

UNIQ_SET = set(UNIQUES)

UNIQUES.sort()

def is_uniq(name):
  return name in UNIQ_SET

def how_deep(name):
  if name in HARD_UNIQUES:
    return 3
  if name in MEDIUM_UNIQUES:
    return 2
  return 1
