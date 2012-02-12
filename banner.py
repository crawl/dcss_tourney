#! /usr/bin/python

from loaddb import query_first_def, query_first, query_do, query_rows, query_rows_with_ties
import crawl
import query

def player_has_banner(c, player, banner):
  return query_first_def(c, None,
                         '''SELECT banner FROM player_banners
                             WHERE player = %s AND banner = %s''',
                         player, banner)

def count_recipients(c, banner):
  return query_first(c, '''SELECT COUNT(*) FROM player_banners
                         WHERE banner = %s''', banner)

def flush_temp_banners(c):
  query_do(c, '''DELETE FROM player_banners WHERE temp = true''')

def award_banner(c, player, banner, prestige, temp=False):
  if player_has_banner(c, player, banner):
    query_do(c, '''UPDATE player_banners
                   SET prestige = %s
                   WHERE player = %s AND banner = %s AND prestige < %s''',
             prestige, player, banner, prestige)
  else:
    query_do(c, '''INSERT INTO player_banners VALUES (%s, %s, %s, %s)''',
             player, banner, prestige, temp)

def pantheon(c, player):
  distinct_gods = query.player_distinct_gods(c, player) 
  if len(distinct_gods) == len(crawl.GODS) - 2:
    award_banner(c, player, 'elyvilon', 7)

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
    award_banner(c, r[0], 'top_player_Nth:%d' % (nth + 1), 1000, temp=True)
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
    award_clan_banner(c, r[0], 'top_clan_Nth:%d' % (nth + 1), 100)
    return True
  query.do_place_numeric(rows, do_banner)
