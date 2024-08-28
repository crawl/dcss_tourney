UNIQUES = ["Agnes", "Aizul", "Amaemon", "Antaeus", "Arachne", "Asmodeus",
           "Asterion", "Azrael", "Bai Suzhen", "Blorkula the Orcula", "Boris",
           "Cerebov", "Crazy Yiuf", "Dispater", "Dissolution", "Donald",
           "Dowan", "Duvessa", "Edmund", "the Enchantress", "Ereshkigal",
           "Erica", "Erolcha", "Eustachio", "Fannar", "Frances", "Frederick",
           "Gastronok", "Geryon", "Gloorx Vloq", "Grinder", "Grum", "Grunn",
           "Harold", "Ignacio", "Ijyb", "Ilsuiw", "Jeremiah", "Jessica",
           "Jorgrun", "Jory", "Joseph", "Josephine", "Josephina", "Khufu",
           "Kirke", "the Lernaean hydra", "Lodul", "Lom Lobon", "Louise",
           "Maggie", "Mara", "Margery", "Maurice", "Menkaure", "Mennas",
           "Mlioglotl", "Mnoleg", "Murray", "Natasha", "Nergalle", "Nessos",
           "Nikola", "Norris", "Parghit", "Pargi", "Pikel", "Polyphemus",
           "Prince Ribbit", "Psyche", "Robin", "Roxanne", "the Royal Jelly",
           "Rupert", "Saint Roka", "the Serpent of Hell", "Sigmund", "Snorg",
           "Sojobo", "Sonja", "Terence", "Tiamat", "Urug", "Vashnia", "Vv",
           "Wiglaf", "Xak'krixis", "Xtahua", "Zenata"]

HARD_UNIQUES = ["Antaeus", "Asmodeus", "Boris", "Cerebov", "Dispater",
                "Dissolution", "the Enchantress", "Ereshkigal", "Frederick",
                "Geryon", "Gloorx Vloq", "Grunn", "Ignacio", "Josephina",
                "Khufu", "Lom Lobon", "Mara", "Margery", "Mennas", "Mnoleg",
                "Murray", "Parghit" "the Royal Jelly", "the Serpent of Hell",
                "Sojobo", "Tiamat", "Wiglaf", "Xtahua", "Zenata"]

MEDIUM_UNIQUES = ["Agnes", "Aizul", "Amaemon", "Arachne", "Asterion",
                  "Azrael", "Bai Suzhen", "Donald", "Frances", "Gastronok",
                  "Ilsuiw", "Jory", "Jorgrun", "Josephine", "Kirke", "Lodul",
                  "Louise", "the Lernaean hydra", "Mlioglotl", "Nergalle",
                  "Nessos", "Nikola", "Norris", "Polyphemus", "Roxanne",
                  "Rupert", "Saint Roka", "Sonja", "Snorg", "Urug", "Vashnia",
                  "Xak'krixis"]

EASY_UNIQUES = ["Blorkula the Orcular", "Crazy Yiuf", "Dowan", "Duvessa",
                "Edmund", "Erica", "Erolcha", "Eustachio", "Fannar", "Grinder",
                "Grum", "Harold", "Ijyb", "Jeremiah", "Jessica", "Joseph",
                "Maggie", "Maurice", "Menkaure", "Natasha", "Pikel",
                "Prince Ribbit", "Psyche", "Purgy", "Robin", "Sigmund",
                "Terence"]

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
