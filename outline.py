#!/usr/bin/python

import loaddb
import query
import banner

import logging
from logging import debug, info, warn, error
import crawl_utils
import crawl
import uniq

from loaddb import query_do, query_first_col, query_rows
from query import count_points, assign_points, assign_team_points, wrap_transaction
from query import log_temp_points, log_temp_team_points, get_points

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
  def logfile_event(self, cursor, logdict):
    act_on_logfile_line(cursor, logdict)

  def milestone_event(self, cursor, milestone):
    act_on_milestone(cursor, milestone)

  def cleanup(self, db):
    cursor = db.cursor()
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

  if mile['xl'] >= 13:
    banner.award_banner(c, player, 'okawaru', 1)

  miletype = milestone_type(mile)
  if miletype == 'uniq' and not milestone_desc(mile).startswith('banished '):
    do_milestone_unique(c, mile)
  elif miletype == 'rune':
    do_milestone_rune(c, mile)
  elif miletype == 'ghost':
    do_milestone_ghost(c, mile)
  elif miletype == 'br.enter':
    do_milestone_br_enter(c, mile)
  elif miletype == 'br.mid':
    do_milestone_br_mid(c, mile)
  elif miletype == 'br.end':
    do_milestone_br_end(c, mile)
  elif miletype == 'god.maxpiety':
    do_milestone_max_piety(c, mile)
  elif miletype == 'zig.enter':
    do_milestone_zig_enter(c, mile)
  elif miletype == 'zig':
    do_milestone_zig(c, mile)
  elif miletype == 'zig.exit':
    do_milestone_zig_exit(c, mile)
  elif miletype == 'abyss.exit':
    do_milestone_abyss_exit(c, mile)

def do_milestone_unique(c, mile):
  """This function takes a parsed milestone known to commemorate the death of
  a unique, and checks to see if the player has already killed the unique.
  If so, it does nothing; if not, it marks that the player has killed the
  unique, and checks to see if the player has killed all uniques. If so,
  the player may be awarded points if they are one of the first to do so."""
  unique = loaddb.extract_unique_name(mile['milestone'])
  # DB already has the record for this kill, so == 1 => first kill.
  if query.count_player_unique_kills(c, mile['name'], unique) > 1:
    return
  assign_points(c, "unique", mile['name'], 5)

def do_milestone_rune(c, mile):
  """Give out 30/N points for the Nth time a player finds a rune, and also give out banners."""
  # Check if this player already found this kind of rune. Remember the db
  # is already updated, so for the first rune the count will be 1.
  rune = loaddb.extract_rune(mile['milestone'])
  num_rune = query.player_count_runes(c, mile['name'], rune)
  rune_points = (30 + num_rune - 1) / num_rune
  assign_points(c, "rune:" + rune, mile['name'], rune_points)
  player = mile['name']
  runes_found = query.player_count_distinct_runes(c, player)
  if runes_found == crawl.NRUNES:
    banner.award_banner(c, player, 'sif', 3)
  elif runes_found >= 5:
    banner.award_banner(c, player, 'sif', 2)
  if rune == 'golden' and num_rune == 1:
    banner.award_banner(c, player, 'fedhas', 2)
  if nemelex.is_nemelex_choice(mile['char'], mile['time']):
    ban = 'nemelex:' + mile['char']
    banner.award_banner(c, player, ban, 2)
  if not query.did_reach_d14(c, player, mile['start'], mile['time']):
    if mile['urune'] >= 4:
      banner.award_banner(c, player, 'the_shining_one', 3)
    elif mile['urune'] >= 2:
      banner.award_banner(c, player, 'the_shining_one', 2)
    else:
      banner.award_banner(c, player, 'the_shining_one', 1)

def do_milestone_ghost(c, mile):
  """When you kill a player ghost, you get two clan points! Otherwise this
  isn't terribly remarkable."""
  if not mile['milestone'].startswith('banished'):
    assign_team_points(c, "ghost", mile['name'], 2)

def do_milestone_br_enter(c, mile):
  """Five points for the first time you get each br.enter milestone (includes
  portal vaults). Also give out banners."""
  if query.player_count_br_enter(c, mile['name'], mile['noun']) == 1:
    assign_points(c, "branch:enter", mile['name'], 5)
  if mile['noun'] == 'Crypt':
    banner.award_banner(c, mile['name'], 'fedhas', 1)
  elif mile['noun'] in ['Vault', 'Snake', 'Swamp', 'Shoals', 'Spider', 'Pan', 'Slime',
                      'Tomb', 'Dis', 'Tar', 'Coc', 'Geh']:
    banner.award_banner(c, mile['name'], 'sif', 1)
    if mile['noun'] in ['Pan', 'Dis', 'Tar', 'Coc', 'Geh']:
      banner.award_banner(c, mile['name'], 'zin', 1)
  elif mile['noun'] == 'Hell':
    if not query.game_did_visit_lair(c, mile['name'], mile['start'], mile['time']):
      banner.award_banner(c, mile['name'], 'kikubaaqudgha', 1)

def do_milestone_br_mid(c, mile):
  if mile['dur'] <= 1620:
    banner.award_banner(c, mile['name'], 'makhleb', 1)

def do_milestone_br_end(c, mile):
  """Five points for the first time you get each br.enter milestone (includes
  portal vaults)."""
  if mile['noun'] == 'D':
    if mile['dur'] <= 1620:
      if mile['raceabbr'] in ['Ce','Fe','Sp']:
        banner.award_banner(c, mile['name'], 'makhleb', 2)
      else:
        banner.award_banner(c, mile['name'], 'makhleb', 3)
  if mile['noun'] == 'Lair':
    if not banner.player_has_banner(c, mile['name'], 'ashenzari', 1):
      if not query.did_exit_branch(c, 'Lair', mile['name'], mile['start'], mile['time']):
        banner.award_banner(c, mile['name'], 'ashenzari', 1)
  if query.player_count_br_end(c, mile['name'], mile['noun']) <= 1:
    assign_points(c, "branch:end", mile['name'], 5)

def do_milestone_max_piety(c, mile):
  if query.record_max_piety(c, mile['name'], mile['start'], mile['noun']):
    assign_points(c, "champion", mile['name'], 10)

def do_milestone_zig_enter(c, mile):
  banner.award_banner(c, mile['name'], 'xom', 1)

def do_milestone_zig(c, mile):
  if mile['place'] == 'Zig:14':
    banner.award_banner(c, mile['name'], 'xom', 2)

def do_milestone_zig_exit(c, mile):
  if mile['place'] == 'Zig:27':
    banner.award_banner(c, mile['name'], 'xom', 3)

def do_milestone_abyss_exit(c, mile):
  god = mile.get('god') or 'No God'
  if god != 'Lugonu' and not query.did_worship_god(c, 'Lugonu', mile['name'], mile['start'], mile['time']):
    if query.did_get_rune(c, 'abyssal', mile['name'], mile['start'], mile['time']):
      if mile['xl'] < 13:
        prestige = 3
      else:
        prestige = 2
    else:
      prestige = 1
    banner.award_banner(c, mile['name'], 'lugonu', prestige)

def act_on_logfile_line(c, this_game):
  """Actually assign things and write to the db based on a logfile line
  coming through. All lines get written to the db; some will assign
  irrevocable points and those should be assigned immediately. Revocable
  points (high scores, lowest dungeon level, fastest wins) should be
  calculated elsewhere."""
  if game_is_win(this_game):
    crunch_winner(c, this_game) # lots of math to do for winners

  crunch_misc(c, this_game)

  if loaddb.is_ghost_kill(this_game):
    ghost = loaddb.extract_ghost_name(this_game['killer'])
    XL = this_game['xl']
    if XL > 5:
      assign_team_points(c, "gkill", ghost, (XL - 5))

def crunch_misc(c, g):
  player = g['name']
  ktyp = g['ktyp']

  if ktyp != 'winning':
    query.kill_active_streak(c, player)

  if g['xl'] >= 13:
    banner.award_banner(c, player, 'okawaru', 1)

  if g['xl'] >= 9 and nemelex.is_nemelex_choice(g['char'],g['start']):
    ban = 'nemelex:' + g['char']
    banner.award_banner(c, player, ban, 1)
  if g['xl'] >= 9 and query.check_xl9_streak(c, player, g['start']):
    banner.award_banner(c, player, 'cheibriados', 1)
  if g['sc'] >= 1000:
    og = query.previous_combo_highscore(c, g)
    if og and og[0] != player and og[1] >= 1000 and og[1] < g['sc']:
      banner.award_banner(c, player, 'trog', 1)

  killer = loaddb.strip_unique_qualifier(g.get('killer') or '')
  if uniq.is_uniq(killer):
    query_do(c,
             '''INSERT INTO deaths_to_uniques
                            (player, uniq, start_time, end_time)
                     VALUES (%s, %s, %s, %s)''',
             player, killer, g['start'], g['end'])
    cuniqdeaths = query.count_deaths_to_distinct_uniques(c, player)
    olduniqdeaths = query.lookup_deaths_to_distinct_uniques(c, player)
    if cuniqdeaths > olduniqdeaths:
      query.update_deaths_to_distinct_uniques(c, player, cuniqdeaths,
                                              g['end'])

  #if g.has_key('maxskills'):
  #  maxed_skills = g['maxskills'].split(",")
  #  for sk in maxed_skills:
  #    query.register_maxed_skill(c, player, sk)
  #if g.has_key('fifteenskills'):
  #  fifteen_skills = g['fifteenskills'].split(",")
  #  for sk in fifteen_skills:
  #    if sk in crawl.MAGIC_SKILLS:
  #      query.register_fifteen_skill(c, player, sk)

def repeat_race_class(char1, char2):
  """Returns the number of race/class that the two chars have in common."""
  repeats = 0
  if char1[0:2] == char2[0:2]:
    repeats += 1
  if char1[2:] == char2[2:]:
    repeats += 1
  return repeats

# Streak length is currently defined to be 
# min(# of distinct races, # of distinct classes).
def compute_streak_length(previous_chars, char):
  all_chars = previous_chars + [char,]
  races = set([c[0:2] for c in all_chars])
  classes = set([c[2:] for c in all_chars])
  return min(len(races), len(classes))

def game_is_win(g):
  return g.has_key('ktyp') and g['ktyp'] == 'winning'

def game_player(g):
  return g['name']

def game_end_time(g):
  return g['end']

def game_start_time(g):
  return g['start']

def game_character(g):
  return g['char']

def crunch_winner(c, game):
  """A game that wins could assign a variety of irrevocable points for a
  variety of different things. This function needs to calculate them all."""

  player = game['name']
  charabbrev = game_character(game)
  game_end = game_end_time(game)

  # 20 clan points for first win for a particular combo in the tournament.
  if query.first_win_for_combo(c, charabbrev, game_end):
    assign_team_points(c, "combo_first_win:" + charabbrev, player, 20)

  # Award Okawaru banners for wins.
  banner.award_banner(c, player, 'okawaru', 2)
  if (game['turn'] < 50000):
    banner.award_banner(c, player, 'okawaru', 3)

  if not query.game_did_visit_lair(c, player, game_start_time(game)):
    if not query.game_did_visit_branch(c, player, game_start_time(game)):
      # 50 bonus points for winning without doing any branches.
      assign_points(c, 'branchless_win', player, 50)
      # And the banner:
      banner.award_banner(c, player, 'kikubaaqudgha', 3)
    else:
      # Just 20 bonus points for winning without doing Lair.
      assign_points(c, 'lairless_win', player, 20)
      # And the banner:
      banner.award_banner(c, player, 'kikubaaqudgha', 2)

  ash_prestige = query.check_ash_banners(c, player, game_start_time(game))
  if ash_prestige >= 2:
    banner.award_banner(c, player, 'ashenzari', ash_prestige)

  ogame = query.previous_combo_highscore(c, game)
  if ogame and ogame[0] != player and ogame[2] == 'winning' and ogame[1] < game['sc']:
    banner.award_banner(c, player, 'trog', 2)
  if game['sc'] >= 10000000:
    ogame = query.previous_species_highscore(c, game)
    if ogame and ogame[1] >= 10000000 and ogame[1] < game['sc'] and ogame[0] != player:
      banner.award_banner(c, player, 'trog', 3)
    ogame = query.previous_class_highscore(c, game)
    if ogame and ogame[1] >= 10000000 and ogame[1] < game['sc'] and ogame[0] != player:
      banner.award_banner(c, player, 'trog', 3)

  debug("%s win (%s), runes: %d" % (player, charabbrev, game.get('urune') or 0))

  if nemelex.is_nemelex_choice(charabbrev, game_end):
    ban = 'nemelex:' + charabbrev
    if banner.count_recipients(c, ban, 3) < 5:
      if not banner.player_has_banner(c, player, ban, 3):
        assign_points(c, ban, player, 75)
        banner.award_banner(c, player, ban, 3)

  if is_all_runer(game):
    all_allruners = number_of_allruners_before(c, game)
    assign_points(c, "nth_allrune_win:%d" % (all_allruners + 1),
                  game['name'],
                  get_points(all_allruners, 200, 100, 50))

    # If this is my first all-rune win, 50 points!
    #if query.count_wins(c, player = game['name'],
    #                    runes = query.MAX_RUNES,
    #                    before = game_end) == 0:
    #  assign_points(c, "my_1st_all_rune_win", game['name'], 50)

  previous_wins = query.count_wins(c, before = game_end)
  assign_points(c,
                "nth_win:%d" % (previous_wins + 1),
                game['name'], get_points(previous_wins, 200, 100, 50))

  my_wins = query.get_winning_games(c, player = game['name'],
                                    before = game_end)
  n_my_wins = len(my_wins)

  if n_my_wins == 0:
    # First win! I bet you don't have a streak
    assign_points(c, "my_1st_win", game['name'], 100)

  else:
    # If the new win is a different race/class from a previous win, bonus!
    for x in my_wins:
      if repeat_race_class(x['charabbrev'], game['char']) == 0:
        assign_points(c, "my_2nd_win_norep", game['name'], 50, False)

  streak_wins = query.wins_in_streak_before(c, game['name'], game_end)
  debug("%s win (%s), previous games in streak: %s" %
        (game['name'], game['char'], streak_wins))
  if not streak_wins:
    query.kill_active_streak(c, player)
    streak_len = -1
  else:
    # Award banner.
    banner.award_banner(c, player, 'cheibriados', 2)
    # This length could be 1 even though it involves at least two games, beware!
    streak_len = compute_streak_length(streak_wins, game['char'])
    if len(streak_wins) >= 3:
      if compute_streak_length(streak_wins[-3:], game['char']) == 4:
        banner.award_banner(c, player, 'cheibriados', 3)
    streak_species = 'streak:species:'+(game['char'][0:2])
    streak_class = 'streak:class:'+(game['char'][2:])
    # 75 points for streak games, but only if they are with a new race and class.
    assign_points(c, streak_species, game['name'], 60, False)
    assign_points(c, streak_class, game['name'], 30, False)
  query.update_active_streak(c, player, game_end, streak_len)

  if streak_len > 1:
    # Update the streaks table. We're still in the logfile transaction
    # here, so it's safe.
    if streak_len > loaddb.longest_streak_count(c, game['name']):
      loaddb.update_streak_count(c, game, streak_len)

  # Assign points for new personal records.
  assign_points(c, 'my_low_turncount_win', game['name'], 5000000/game['turn'], False)
  assign_points(c, 'my_low_realtime_win', game['name'], 1250000/game['dur'], False)
  assign_points(c, 'my_highscore_win', game['name'], game['sc']/120000, False)

  # Assign race/class points, based on the games won before the start
  # of the given win.
  game_start = game_start_time(game)
  wins_before = query.count_wins(c, before=game_start)
  species_wins_before = query.count_wins(c, before=game_start, raceabbr=game['char'][0:2])
  class_wins_before = query.count_wins(c, before=game_start, classabbr=game['char'][2:])
  assign_points(c, 'species_win:' + game['char'][0:2], game['name'], query.race_formula(wins_before, species_wins_before), False)
  assign_points(c, 'class_win:' + game['char'][2:], game['name'], query.class_formula(wins_before, class_wins_before), False)
  # and gods also
  game_god = query.get_game_god(c, game)
  banner_god = game_god.lower().replace(' ', '_')
  if (not game_god == 'faithless'):
    query.record_won_god(c, game['name'], game['end'], game_god)
    god_wins_before = query.count_god_wins(c, game_god, game_start)
    assign_points(c, 'god_win:' + banner_god, game['name'], query.god_formula(wins_before, god_wins_before), False)

def is_all_runer(game):
  """Did this game get every rune? This _might_ require checking the milestones
  associated with the start time..."""
  return game['urune'] == query.MAX_RUNES

def number_of_allruners_before(c, game):
  """How many all-runers happened before this game? We can stop at 3."""
  return query.count_wins(c, runes = query.MAX_RUNES, before = game['end'])

###################### Additional scoring math ##########################

def record_points(point_map, player, points, team_points):
  lplayer = player.lower()
  pdef = point_map.get(lplayer) or { 'team': 0, 'you': 0 }
  pdef[team_points and 'team' or 'you'] += points
  point_map[lplayer] = pdef

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

def award_temp_trophy(c, point_map,
                      player_rows, key, points,
                      can_share_places=False, team_points=False):
  place = -1
  rplace = -1
  last_value = None

  def do_points(player, title, points):
    record_points(point_map, player, points, team_points)
    if team_points:
      log_temp_team_points(c, player, title, points)
    else:
      log_temp_points(c, player, title, points)

  def place_title(title_key, nth):
    if '%' in title_key:
      return title_key % (place + 1)
    else:
      return title_key

  npoints = len(points)
  for row in player_rows:
    rplace += 1
    if not can_share_places or row[1] != last_value:
      place = rplace
    if can_share_places:
      last_value = row[1]

    if place >= npoints:
      break

    title = place_title(key, place)
    p = points[place]
    player = row[0]
    do_points(player, title, p)

def apply_point_map(c, pmap):
  for player, points in pmap.iteritems():
    loaddb.update_player_fullscore(c, player,
                                   points['you'],
                                   points['team'])

def check_temp_trophies(c, pmap):
  award_temp_trophy(c, pmap, query.player_hare_candidates(c),
                    "last_win", [100])

  award_temp_trophy(c, pmap, query.player_streak_best(c),
                    'top_streak:%d', [200, 100, 50])

  award_temp_trophy(c, pmap, query.get_top_unique_killers(c),
                    'top_unique_killer:%d', [50, 20, 10])

#  award_temp_trophy(c, pmap, query.player_pacific_win_best(c),
#                    'top_pacific_win:%d', [200, 100, 50],
#                    team_points=True)

  # [snark] xl1 dive disabled for 2010 tourney.
  #award_temp_trophy(c, pmap, query.player_xl1_dive_best(c),
  #                  'xl1_dive_rank:%d', [50, 20, 10],
  #                  team_points=True)

  award_temp_trophy(c, pmap, query.player_hs_combo_best(c),
                    'combo_scores_Nth:%d', [200, 100, 50],
                    can_share_places=True, team_points=True)

  award_temp_trophy(c, pmap, query.get_top_ziggurats(c),
                    'zig_rank:%d', [100, 50, 20], team_points=True)

  award_temp_trophy(c, pmap, query.player_rune_dive_best(c),
                    'rune_dive_rank:%d', [50, 20, 10], team_points=True)

  award_temp_trophy(c, pmap, query.player_deaths_to_uniques_best(c),
                    'deaths_to_uniques_Nth:%d', [50, 20, 10],
                    can_share_places=False,
                    team_points=True)

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
                                       '''SELECT player FROM fivefives_nine'''),
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
                                       '''SELECT player FROM kunique_times
                                          WHERE nuniques >= 65'''),
                       3)
  award_player_banners(c, 'yredelemnul',
                       query_first_col(c,
                                       '''SELECT player FROM kunique_times
                                          WHERE nuniques >= 45'''),
                       2)
  award_player_banners(c, 'yredelemnul',
                       query_first_col(c,
                                       '''SELECT player FROM kunique_times
                                          WHERE nuniques >= 25'''),
                       1)
  rows = query_rows(c, '''SELECT * FROM nearby_uniques''')
  for r in rows:
    a = uniq.how_deep(r[1])
    b = uniq.how_deep(r[2])
    d = 3 - (r[4] - r[3])
    if b < a:
      a = b
    if d < a:
      a = d
    banner.award_banner(c, r[0], 'vehumet', a)

def check_misc_points(c, pmap):
  def award_misc_points(key, multiplier, rows):
    for r in rows:
      player = r[0]
      points = r[1] * multiplier
      record_points(pmap, player, points, team_points=False)
      log_temp_points(c, player, key % r[1], points)

  award_misc_points('high_score:combo:%d', 5, query.all_hs_combos(c))
  award_misc_points('high_score:combo_win:%d', 5, query.all_hs_combo_wins(c))
  award_misc_points('high_score:species:%d', 20, query.all_hs_species(c))
  award_misc_points('high_score:class:%d', 10, query.all_hs_classes(c))

def compute_player_only(c):
  for p in query.get_players(c):
    points = query.player_specific_points(c, p)
    loaddb.update_player_only_score(c, p, points)

def safe_update_player_scores(c):
  players = query.get_players(c)

  query.audit_flush_player(c)
  banner.flush_temp_banners(c)

  pmap = { }

  for p in players:
    record_points(pmap, p, 0, team_points=False)
    info("Processing banners for " + p)
    banner.process_banners(c, p)

  check_misc_points(c, pmap)
  check_temp_trophies(c, pmap)
  check_banners(c)
  apply_point_map(c, pmap)
  compute_player_only(c)

  # And award overall top banners.
  banner.assign_top_player_banners(c)

  # Check to see whether we need a new Nemelex' Choice.
  if nemelex.need_new_combo(c):
    nemelex.pick_combo(nemelex.eligible_combos(c))
