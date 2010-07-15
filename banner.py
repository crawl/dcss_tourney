#! /usr/bin/python

from loaddb import query_first_def, query_do, query_rows
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
  """Award a banner after checking that the player doesn't already have it."""
  if not player_has_banner(c, player, banner):
    award_banner(c, player, banner, prestige, temp)

def award_banner(c, player, banner, prestige, temp=False):
  query_do(c, '''INSERT INTO player_banners VALUES (%s, %s, %s, %s)''',
           player, banner, prestige, temp)

def pantheon(c, player):
  distinct_gods = [god for god in query.player_distinct_gods(c, player)
                   if god and god != 'No God']
  if len(distinct_gods) == len(crawl.GODS) - 1:
    award_banner(c, player, 'pantheon', 0)

def heretic(c, player):
  gods_renounced = query.player_distinct_renounced_gods(c, player)
  gods_mollified = query.player_distinct_mollified_gods(c, player)
  nrenounced = len(gods_renounced)
  nmollified = len(gods_mollified)
  # [snark] We'll accept one less mollify than renounce because apparently
  # Nemelex mollification produces no milestone (why is this?)
  if (nmollified >= nrenounced - 1 and nrenounced == len(crawl.GODS) - 1):
    award_banner(c, player, 'heretic', 0)

BANNERS = [['pantheon', pantheon],
           ['heretic', heretic],
           ['rune', None],
           ['moose', None],
           ['atheist', None],
           ['scythe', None],
           ['orb', None],
           ['shopaholic', None],
           ['free_will', None],
           ['ghostbuster', None]]

def process_banners(c, player):
  existing_banners = set(query.get_player_banners(c, player))
  for banner in [b for b in BANNERS if b[0] not in existing_banners]:
    if banner[1]:
      banner[1](c, player)

def assign_top_player_banners(c):
  rows = query_rows(c, '''SELECT name, score_full
                            FROM players
                           WHERE score_full > 0
                           ORDER BY score_full DESC, name
                            LIMIT 3''')
  def do_banner(r, nth):
    award_banner(c, r[0], 'top_player_Nth:%d' % (nth + 1), 1000, temp=True)
    return True
  query.do_place_numeric(rows, do_banner)

def award_clan_banner(c, captain, banner, prestige):
  query_do(c, '''INSERT INTO clan_banners VALUES (%s, %s, %s)''',
           captain, banner, prestige)

def flush_clan_banners(c):
  query_do(c, '''TRUNCATE TABLE clan_banners''')

def assign_top_clan_banners(c):
  rows = query_rows(c, '''SELECT owner, total_score
                            FROM teams
                           WHERE total_score > 0
                           ORDER BY total_score DESC, name
                           LIMIT 3''')
  def do_banner(r, nth):
    award_clan_banner(c, r[0], 'top_clan_Nth:%d' % (nth + 1), 1000)
    return True
  query.do_place_numeric(rows, do_banner)
