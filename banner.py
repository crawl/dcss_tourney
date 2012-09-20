#! /usr/bin/python

from loaddb import query_first_def, query_first, query_do, query_rows, query_rows_with_ties
import crawl
import query

def player_has_banner(c, player, banner, prestige):
  return query_first_def(c, None,
                         '''SELECT banner FROM player_banners
                             WHERE player = %s AND banner = %s AND prestige >= %s''',
                         player, banner, prestige)

def count_recipients(c, banner, prestige):
  return query_first(c, '''SELECT COUNT(*) FROM player_banners
                         WHERE banner = %s AND prestige >= %s''', banner, prestige)

def flush_temp_banners(c):
  query_do(c, '''DELETE FROM player_banners WHERE temp = true''')

def award_banner(c, player, banner, prestige, temp=False):
  if player_has_banner(c, player, banner, 0):
    query_do(c, '''UPDATE player_banners
                   SET prestige = %s
                   WHERE player = %s AND banner = %s AND prestige < %s''',
             prestige, player, banner, prestige)
  else:
    query_do(c, '''INSERT INTO player_banners VALUES (%s, %s, %s, %s)''',
             player, banner, prestige, temp)

def pantheon(c, player):
  distinct_gods = query.player_distinct_gods(c, player) 
  if len(distinct_gods) >= 13:
    award_banner(c, player, 'elyvilon', 3)
  elif len(distinct_gods) >= 5:
    award_banner(c, player, 'elyvilon', 2)
  elif len(distinct_gods) >= 1:
    award_banner(c, player, 'elyvilon', 1)

BANNERS = [['elyvilon', pantheon]]

def process_banners(c, player):
  for banner in BANNERS:
    if banner[1]:
      banner[1](c, player)

def assign_top_player_banners(c):
  rows = query_rows_with_ties(c, '''SELECT name, score_full
                            FROM players
                           WHERE score_full > 0''',
                           'score_full', 3, 1)
  def do_banner(r, nth):
    award_banner(c, r[0], '1top_player', 100*(1+nth), temp=True)
    return True
  query.do_place_numeric(rows, do_banner)

def award_clan_banner(c, captain, banner, prestige):
  query_do(c, '''INSERT INTO clan_banners VALUES (%s, %s, %s)''',
           captain, banner, prestige)

def flush_clan_banners(c):
  query_do(c, '''TRUNCATE TABLE clan_banners''')

def assign_top_clan_banners(c):
  rows = query_rows_with_ties(c, '''SELECT owner, total_score
                            FROM teams
                           WHERE total_score > 0''',
                           'total_score', 3, 1)
  def do_banner(r, nth):
    award_clan_banner(c, r[0], '2top_clan', 10*(1+nth))
    return True
  query.do_place_numeric(rows, do_banner)
  def do_saint(r, prestige):
    for player in query.get_saints(c, r[0]):
      award_banner(c, player, 'beogh', prestige, temp=True)
  rows = query_rows_with_ties(c, '''SELECT owner, total_score
                            FROM teams
                           WHERE total_score > 0''',
                           'total_score', 5, 1)
  for r in rows:
    do_saint(r, 3)
  rows = query_rows_with_ties(c, '''SELECT owner, total_score
                            FROM teams
                           WHERE total_score > 0''',
                           'total_score', 20, 1)
  for r in rows:
    do_saint(r, 2)
