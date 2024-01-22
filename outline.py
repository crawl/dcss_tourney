#!/usr/bin/python

import loaddb
import query
import banner

import logging
from logging import debug, info, warn, error
import crawl_utils
import crawl
import uniq

import datetime
import math

from loaddb import query_do, query_first_col, query_rows
from query import wrap_transaction

import nemelex

# So there are a few problems we have to solve:
# 1. Intercepting new logfile events
#    DONE: parsing a logfile line
#    DONE: dealing with deaths
# 2. Intercepting new milestone events
#    DONE: parsing a milestone line
#    How do we write milestone lines into the db?
# 3. DONE: Collecting data from whereis files
# 4. Determining who is the winner of various competitions based on the
#    ruleset: this still needs to be done for the ones that are basically
#    a complicated query.
# 5. Causing the website to be updated with who is currently winning everything
#    and, if necessary, where players are: first priority is a "who is winning
#    the obvious things"

class OutlineListener (loaddb.CrawlEventListener):
  def logfile_event(self, cursor, logdict, filename=None):
    act_on_logfile_line(cursor, logdict, filename)

  def milestone_event(self, cursor, milestone):
    act_on_milestone(cursor, milestone)

  def cleanup(self, db):
    cursor = db.cursor()
    loaddb.support_mysql57(cursor)
    try:
      update_player_scores(cursor)
    finally:
      cursor.close()

class OutlineTimer (loaddb.CrawlTimerListener):
  def run(self, cursor, elapsed):
    update_player_scores(cursor)

LISTENER = [ OutlineListener() ]

# Update player scores every so often.
TIMER = [ ( crawl_utils.UPDATE_INTERVAL, OutlineTimer() ) ]

def milestone_type(m):
  return m['type']

def milestone_desc(m):
  return m['milestone']

def act_on_milestone(c, mile):
  """This function takes a milestone line, which is a string composed of key/
  value pairs separated by colons, and parses it into a dictionary.
  Then, depending on what type of milestone it is (key "type"), another
  function may be called to finish the job on the milestone line. Milestones
  have the same broken :: behavior as logfile lines, yay."""

  player = game_player(mile)

  if mile['goldfound'] >= 1000:
    banner.award_banner(c, player, 'gozag', 1)

  if mile['xl'] >= 9 and nemelex.is_nemelex_choice(mile['char'],mile['start']):
    banner.award_banner(c, player, 'nemelex', 1)

  # hack to handle milestones with no potions_used/scrolls_used fields
  if 'potionsused' not in mile:
    mile['potionsused'] = -1
    mile['scrollsused'] = -1

  miletype = milestone_type(mile)
  if miletype == 'uniq' and not milestone_desc(mile).startswith('banished '):
    do_milestone_unique(c, mile)
  elif miletype == 'rune':
    do_milestone_rune(c, mile)
  elif miletype == 'gem.found':
    do_milestone_gem_found(c, mile)
  elif miletype == 'br.enter':
    do_milestone_br_enter(c, mile)
  elif miletype == 'br.end':
    do_milestone_br_end(c, mile)
  elif miletype == 'god.maxpiety':
    do_milestone_max_piety(c, mile)
  elif miletype == 'zig' or miletype == 'zig.enter':
    do_milestone_zig(c, mile)
  elif miletype == 'zig.exit':
    do_milestone_zig_exit(c, mile)
  elif miletype == 'abyss.enter':
    do_milestone_abyss_enter(c, mile)
  elif miletype == 'abyss.exit':
    do_milestone_abyss_exit(c, mile)
  elif miletype == 'god.mollify':
    do_milestone_mollify(c, mile)

def do_milestone_unique(c, mile):
  """This function takes a parsed milestone known to commemorate the death of
  a unique, and assigns relevant banners."""
  unique = loaddb.extract_unique_name(mile['milestone'])
  if unique == 'Sigmund':
    if not query.did_enter_branch(c, 'Depths', mile['name'], mile['start'], mile['time']):
      banner.award_banner(c, mile['name'], 'the_shining_one', 1)

def do_milestone_rune(c, mile):
  """Give out banners for certain special rune finds."""
  # Check if this player already found this kind of rune. Remember the db
  # is already updated, so for the first rune the count will be 1.
  rune = loaddb.extract_rune(mile['milestone'])
  num_rune = query.player_count_runes(c, mile['name'], rune)
  player = mile['name']
  runes_found = query.player_count_distinct_runes(c, player)
  if mile['dur'] <= 4860:
    banner.award_banner(c, mile['name'], 'makhleb', 2)
  if runes_found == crawl.NRUNES:
    banner.award_banner(c, player, 'ashenzari', 3)
  elif runes_found >= 5:
    banner.award_banner(c, player, 'ashenzari', 2)
  if mile['urune'] == 1:
    if rune == 'silver':
      banner.award_banner(c, player, 'trog', 2)
    elif rune == 'golden':
      banner.award_banner(c, player, 'trog', 3)
  if rune == 'golden' and num_rune == 1:
    banner.award_banner(c, player, 'fedhas', 2)
  if rune == 'silver' and num_rune == 1:
    banner.award_banner(c, player, 'gozag', 2)
  did_ecu = query.did_use_ecumenical_altar(c, mile['name'], mile['start'],
                mile['time'])
  did_renounce = query.did_renounce_god(c, mile['name'], mile['start'],
                        mile['time'])
  if (did_ecu and not did_renounce):
    banner.award_banner(c, player, 'hepliaklqana', 2)

  # The abyssal rune is the only rune that the player can get before the iron
  # rune for Avarice 3.
  if rune == 'iron' and mile['urune'] <= 2:
    other_rune_branches = ['Vaults', 'Shoals', 'Snake', 'Spider', 'Swamp', 'Slime', 'Pan', 'Coc', 'Geh', 'Tar']
    eligible = True
    for br in other_rune_branches:
      if query.did_enter_branch(c, br, player, mile['start'], mile['time']):
        eligible = False
        break
    if eligible:
      banner.award_banner(c, player, 'gozag', 3)

  if nemelex.is_nemelex_choice(mile['char'], mile['time']):
    banner.award_banner(c, player, 'nemelex', 2)
  if not query.did_enter_branch(c, 'Depths', player, mile['start'], mile['time']):
    if mile['urune'] == 6:
      banner.award_banner(c, player, 'the_shining_one', 3)
    elif mile['urune'] >= 4:
      banner.award_banner(c, player, 'the_shining_one', 2)
  #if query.time_from_str(mile['time']) - query.time_from_str(mile['start']) <= datetime.timedelta(hours=27):
  #  banner.award_banner(c, mile['name'], 'oldbanner', 1)
  if rune != 'slimy' and rune != 'abyssal':
    if mile['potionsused'] == 0 and mile['scrollsused'] == 0:
      banner.award_banner(c, mile['name'], 'ru', 3)
  if mile['urune'] == 1:
    if mile['xl'] < 17:
      if (not query.did_sacrifice(c, 'experience', mile['name'], mile['start'], mile['time'])
          and not query.did_worship_god(c, 'Hepliaklqana', mile['name'], mile['start'], mile['time'])):
        banner.award_banner(c, mile['name'], 'vehumet', 2)

def do_milestone_gem_found(c, mile):
  """Give out banners for gems collected."""
  banner.award_banner(c, mile['name'], 'uskayaw', 1)

def do_milestone_br_enter(c, mile):
  """Give out banners for branch entry."""
  if mile['noun'] == 'Crypt':
    banner.award_banner(c, mile['name'], 'fedhas', 1)
  if mile['noun'] in ['Vaults', 'Snake', 'Swamp', 'Shoals', 'Spider', 'Slime',
                      'Tomb', 'Dis', 'Tar', 'Coc', 'Geh']:
    banner.award_banner(c, mile['name'], 'ashenzari', 1)
  if mile['noun'] in ['Pan', 'Dis', 'Tar', 'Coc', 'Geh']:
    banner.award_banner(c, mile['name'], 'zin', 1)
  if mile['noun'] == 'Lair':
    if mile['sk'] == 'Invocations':
      banner.award_banner(c, mile['name'], 'qazlal', 1)
    if query.did_use_ecumenical_altar(c, mile['name'], mile['start'], mile['time']) \
        and not query.did_renounce_god(c, mile['name'], mile['start'], mile['time']):
      banner.award_banner(c, mile['name'], 'hepliaklqana', 1)
  if mile['noun'] == 'Temple':
    if mile['potionsused'] == 0 and mile['scrollsused'] == 0:
      banner.award_banner(c, mile['name'], 'ru', 1)
    if mile['turn'] < 3000:
      banner.award_banner(c, mile['name'], 'wu_jian', 1)
  if mile['noun'] == 'Vaults' and query.player_count_distinct_runes(c, mile['name']) == 0:
    banner.award_banner(c, mile['name'], 'trog', 1)

def do_milestone_br_end(c, mile):
  if mile['noun'] == 'Orc':
    if not query.game_did_visit_lair(c, mile['name'], mile['start'], mile['time']):
      banner.award_banner(c, mile['name'], 'kikubaaqudgha', 1)
  if mile['noun'] == 'Depths':
    if not query.game_did_visit_lair(c, mile['name'], mile['start'], mile['time']):
      banner.award_banner(c, mile['name'], 'kikubaaqudgha', 2)
  if mile['noun'] == 'D':
    if mile['dur'] <= 3240 and mile['race'] != 'Formicid':
      banner.award_banner(c, mile['name'], 'makhleb', 1)
  if mile['noun'] == 'Lair':
    if mile['sklev'] < 13 and mile['race'] != 'Formicid' and mile['race'] != 'Gnoll':
      if not query.did_worship_god(c, 'Ashenzari', mile['name'], mile['start'], mile['time']):
        banner.award_banner(c, mile['name'], 'sif', 1)
    if mile['xl'] < 13 and mile['race'] != 'Formicid':
      if (not query.did_sacrifice(c, 'experience', mile['name'], mile['start'], mile['time'])
          and not query.did_worship_god(c, 'Hepliaklqana', mile['name'], mile['start'], mile['time'])):
        banner.award_banner(c, mile['name'], 'vehumet', 1)
    if mile['potionsused'] == 0 and mile['scrollsused'] == 0:
      banner.award_banner(c, mile['name'], 'ru', 2)
  if mile['noun'] == 'Elf' and mile['turn'] < 12000:
    banner.award_banner(c, mile['name'], 'wu_jian', 2)
  if mile['noun'] == 'Geh' and mile['turn'] < 27000:
    banner.award_banner(c, mile['name'], 'wu_jian', 3)

def do_milestone_max_piety(c, mile):
  query.record_max_piety(c, mile['name'], mile['start'], mile['noun'])
  if mile['noun'] == 'Ru':
    banner.award_banner(c, mile['name'], 'lugonu', 1)
  elif query.did_champion(c, 'Ru', mile['name'], mile['start'], mile['time']):
    banner.award_banner(c, mile['name'], 'lugonu', 2)

# Nothinng for now
def do_milestone_abyss_enter(c, mile):
  return

# on entry or descent
def do_milestone_zig(c, mile):
  banner.award_banner(c, mile['name'], 'xom', 1)
  if mile['place'] == 'Zig:10':
    banner.award_banner(c, mile['name'], 'xom', 2)

def do_milestone_zig_exit(c, mile):
  if mile['place'] == 'Zig:27':
    banner.award_banner(c, mile['name'], 'xom', 3)

def do_milestone_abyss_exit(c, mile):
  god = mile.get('god') or 'No God'
  #if god != 'Lugonu' and not query.did_worship_god(c, 'Lugonu', mile['name'], mile['start'], mile['time']):
  #  if query.did_get_rune(c, 'abyssal', mile['name'], mile['start'], mile['time']):
  #    if mile['xl'] < 16:
  #      prestige = 3
  #    else:
  #      prestige = 2
  #  else:
  #    prestige = 1
  #  banner.award_banner(c, mile['name'], 'oldlugonu', prestige)

def do_milestone_mollify(c, mile):
  god = mile.get('god') or 'No God'
  #if god != mile['noun']:
  #  banner.award_banner(c, mile['name'], 'lugonu', 1)

def act_on_logfile_line(c, this_game, filename):
  """Actually assign things and write to the db based on a logfile line
  coming through. All lines get written to the db; some will assign
  irrevocable points and those should be assigned immediately. Revocable
  points (high scores, lowest dungeon level, fastest wins) should be
  calculated elsewhere."""
  if game_is_win(this_game):
    crunch_winner(c, this_game, filename) # lots of math to do for winners

  crunch_misc(c, this_game)

def crunch_misc(c, g):
  player = g['name']
  ktyp = g['ktyp']


  if g['sc'] >= 27000000:
    banner.award_banner(c, player, 'okawaru', 3)
  elif g['sc'] >= 9000000:
    banner.award_banner(c, player, 'okawaru', 2)
  elif g['sc'] >= 1000000:
    banner.award_banner(c, player, 'okawaru', 1)

  if g['goldfound'] >= 1000:
    banner.award_banner(c, player, 'gozag', 1)

  if g['xl'] >= 9 and nemelex.is_nemelex_choice(g['char'],g['start']):
    banner.award_banner(c, player, 'nemelex', 1)
  if g['xl'] >= 9 and query.check_xl9_streak(c, player, g['start']):
    banner.award_banner(c, player, 'cheibriados', 1)
  if g['sc'] >= 1000:
    og = query.previous_combo_highscore(c, g)
    if og and og[0] != player and og[1] >= 1000 and og[1] < g['sc']:
      banner.award_banner(c, player, 'dithmenos', 1)

  killer = loaddb.strip_unique_qualifier(g.get('killer') or '')

def repeat_race_class(char1, char2):
  """Returns the number of race/class that the two chars have in common."""
  repeats = 0
  if char1[0:2] == char2[0:2]:
    repeats += 1
  if char1[2:] == char2[2:]:
    repeats += 1
  return repeats

def game_is_win(g):
  return 'ktyp' in g and g['ktyp'] == 'winning'

def game_player(g):
  return g['name']

def game_end_time(g):
  return g['end']

def game_start_time(g):
  return g['start']

def game_character(g):
  return g['char']

def crunch_winner(c, game, filename):
  """A game that wins could assign a variety of irrevocable points for a
  variety of different things. This function needs to calculate them all."""

  player = game['name']
  charabbrev = game_character(game)
  game_start = game_start_time(game)
  game_end = game_end_time(game)

  if game['dur'] <= 10800:
    banner.award_banner(c, player, 'makhleb', 3)

  if game['sk'] == 'Invocations':
    banner.award_banner(c, player, 'qazlal', 2)
    if query.player_count_invo_titles(c, player) >= 3:
      banner.award_banner(c, player, 'qazlal', 3)

  if query.check_ru_abandonment_game(c, player, game_start_time(game)):
    banner.award_banner(c, player, 'lugonu', 3)

  if not query.game_did_visit_lair(c, player, game_start_time(game)):
    if not query.game_did_visit_branch(c, player, game_start_time(game)):
      banner.award_banner(c, player, 'kikubaaqudgha', 3)

  if game['race'] != 'Gnoll' and game['sklev'] < 20:
    if not query.did_worship_god(c, 'Ashenzari', player, game['start'], game['end']):
      if game['sklev'] < 13:
        banner.award_banner(c, player, 'sif', 3)
      else:
        banner.award_banner(c, player, 'sif', 2)

  if game['xl'] < 22:
    if (not query.did_sacrifice(c, 'experience', player, game['start'], game['end'])
        and not query.did_worship_god(c, 'Hepliaklqana', game['name'], game['start'], game['end'])):
      banner.award_banner(c, player, 'vehumet', 3)

  #cutoff = query.time_from_str(game['end']) - datetime.timedelta(hours=27)
  #if query.time_from_str(game['start']) > cutoff:
  #  if query.count_wins(c, player = game['name'], before = game_end, after = cutoff) > 0:
  #    banner.award_banner(c, player, 'oldbanner', 3)
  #  else:
  #    banner.award_banner(c, player, 'oldbanner', 2)

  ogame = query.previous_combo_highscore(c, game)
  if ogame and ogame[0] != player and ogame[2] == 'winning' and ogame[1] < game['sc']:
    banner.award_banner(c, player, 'dithmenos', 2)
  if game['sc'] >= 10000000:
    ogame = query.previous_species_highscore(c, game)
    if ogame and ogame[1] >= 10000000 and ogame[1] < game['sc'] and ogame[0] != player:
      banner.award_banner(c, player, 'dithmenos', 3)
    ogame = query.previous_class_highscore(c, game)
    if ogame and ogame[1] >= 10000000 and ogame[1] < game['sc'] and ogame[0] != player:
      banner.award_banner(c, player, 'dithmenos', 3)

  debug("%s win (%s), runes: %d" % (player, charabbrev, game.get('urune') or 0))

  if nemelex.is_nemelex_choice(charabbrev, game_end) \
       and not nemelex.player_has_nemelex_win(c, player, charabbrev):
    nemelex.award_nemelex_win(c, game, filename)
    banner.award_banner(c, player, 'nemelex', 3)

  if query.did_use_ecumenical_altar(c, game['name'], game['start'], game['end']) \
      and not query.did_renounce_god(c, game['name'], game['start'], game['end']):
    banner.award_banner(c, game['name'], 'hepliaklqana', 3)

  if is_all_runer(game):
    all_allruners = number_of_allruners_before(c, game)

  previous_wins = query.count_wins(c, before = game_end)

  my_wins = query.get_winning_games(c, player = game['name'],
                                    before = game_end)
  n_my_wins = len(my_wins)

  if n_my_wins == 0:
    # First win!
    query.assign_nonrep_win(c, game['name'], 1)
  else:
    for x in my_wins:
      if repeat_race_class(x['charabbrev'], game['char']) == 0:
        query.assign_nonrep_win(c, game['name'], 2)

  did_streak = query.win_is_streak(c, game['name'], game_start)
  if did_streak:
    # Award banner.
    banner.award_banner(c, player, 'cheibriados', 2)

  game_god = query.get_game_god(c, game)
  banner_god = game_god.lower().replace(' ', '_')
  if (not game_god == 'faithless'):
    query.record_won_god(c, game['name'], game_god)

  if game.get('igem') == query.MAX_GEMS:
      banner.award_banner(c, player, 'uskayaw', 3)
  elif game.get('igem') >= 3:
      banner.award_banner(c, player, 'uskayaw', 2)

def is_all_runer(game):
  """Did this game get every rune? This _might_ require checking the milestones
  associated with the start time..."""
  return game['urune'] == query.MAX_RUNES

def number_of_allruners_before(c, game):
  """How many all-runers happened before this game? We can stop at 3."""
  return query.count_wins(c, runes = query.MAX_RUNES, before = game['end'])

###################### Additional scoring math ##########################

def player_additional_score(c, player, pmap):
  """Calculates the player's total score, including unchanging score and the
  current volatile score. Best-of-X trophies are not calculated here."""
  banner.process_banners(c, player)

def update_player_scores(c):
  wrap_transaction(safe_update_player_scores)(c)

def award_player_banners(c, banner_name, players, prestige=0, temp=False):
  if players:
    for p in players:
      banner.award_banner(c, p, banner_name, prestige, temp)

def check_banners(c):
  award_player_banners(c, 'zin',
                       query_first_col(c, '''SELECT player
                                             FROM all_hellpan_kills'''),
                       3)
  award_player_banners(c, 'zin',
                       query_first_col(c, '''SELECT player
                                             FROM have_hellpan_kills'''),
                       2)
  award_player_banners(c, 'jiyva',
                       query_first_col(c,
                                       '''
SELECT player, COUNT(DISTINCT MID(charabbrev,1,2)) AS race_count,
               COUNT(DISTINCT MID(charabbrev,3,2)) AS class_count
FROM
(SELECT player, charabbrev FROM games WHERE xl>=9
UNION
SELECT player, charabbrev FROM milestones WHERE xl>=9) AS T
GROUP BY player
HAVING race_count >= 5 AND class_count >= 5'''),
                       1)
  award_player_banners(c, 'jiyva',
                       query_first_col(c,
                                       '''SELECT player FROM fivefives_rune'''),
                       2)
  award_player_banners(c, 'jiyva',
                       query_first_col(c,
                                       '''SELECT player FROM fivefives_win'''),
                       3)
  award_player_banners(c, 'fedhas',
                       query_first_col(c,
                                       '''SELECT player FROM orbrun_tomb'''),
                       3)
  award_player_banners(c, 'yredelemnul',
                       query_first_col(c,
                                       '''SELECT player FROM unique_kill_count
                                          WHERE score >= 81'''),
                       3)
  award_player_banners(c, 'yredelemnul',
                       query_first_col(c,
                                       '''SELECT player FROM unique_kill_count
                                          WHERE  score >= 54'''),
                       2)
  award_player_banners(c, 'yredelemnul',
                       query_first_col(c,
                                       '''SELECT player FROM unique_kill_count
                                          WHERE score >= 27'''),
                       1)

def update_streaks(c):
  # streak handling
  all_streaks = query.list_all_streaks(c)
  # give out streak points and handle Chei III here so we don't have to
  # recompute all streaks yet again
  for streak in all_streaks:
    if streak['length'] > 1:
      query.update_streak(c,streak)
    if streak['length'] < 4:
      continue
    l = len(streak['games'])
    for i in range(l-3):
      if query.compute_streak_length(streak['games'][i:i+4]) == 4:
        banner.award_banner(c, streak['player'], 'cheibriados', 3)
        break

def safe_update_player_scores(c):
  players = query.get_players(c)

  banner.flush_temp_banners(c)

  pmap = { }

  for p in players:
    info("Processing banners for " + p)
    banner.process_banners(c, p)

  check_banners(c)
  update_streaks(c)
  query.update_all_player_ranks(c)
  query.update_player_scores(c)

  # And award overall top banners.
  banner.assign_top_player_banners(c)

  # Check to see whether we need a new Nemelex' Choice.
  if nemelex.need_new_combo(c):
    nemelex.pick_combo(nemelex.eligible_combos(c))
