#! /usr/bin/python

from loaddb import query_first_def, query_do
import crawl
import query

def player_has_banner(c, player, banner):
  return query_first_def(c, None,
                         '''SELECT banner FROM player_banners
                             WHERE player = %s AND banner = %s''',
                         player, banner)

def flush_temp_banners(c):
  query_do(c, '''DELETE FROM player_banners WHERE temp = true''')

def safe_award_banner(c, player, banner, prestige, temp=False):
  if not player_has_banner(c, player, banner):
    award_banner(c, player, banner, prestige, temp)

def award_banner(c, player, banner, prestige, temp=False):
  query_do(c, '''INSERT INTO player_banners VALUES (%s, %s, %s, %s)''',
           player, banner, prestige, temp)

def pantheon(c, player):
  distinct_gods = [god for god in query.player_distinct_gods(c, player)
                   if god and god != 'No God']
  if len(distinct_gods) == len(crawl.GODS) - 1:
    award_banner(c, player, 'Pantheon', 0)

def heretic(c, player):
  gods_renounced = query.player_distinct_renounced_gods(c, player)
  gods_mollified = query.player_distinct_mollified_gods(c, player)
  if (len(gods_mollified) == len(gods_renounced)
      and len(gods_mollified) == len(crawl.GODS) - 1):
    award_banner(c, player, 'Heretic', 0)

BANNERS = [['Pantheon', pantheon],
           ['Heretic', heretic],
           ['Rune', None],
           ['Moose & Squirrel', None],
           ['Atheist', None],
           ['Scythe', None],
           ['Orb', None],
           ['Shopaholic', None],
           ['Free Will', None],
           ['Ghostbuster', None]]

def process_banners(c, player):
  existing_banners = set(query.get_player_banners(c, player))
  for banner in [b for b in BANNERS if b[0] not in existing_banners]:
    if banner[1]:
      banner[1](c, player)
