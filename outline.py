#!/usr/bin/python

import loaddb
import query
import banner

import logging
from logging import debug, info, warn, error
import crawl_utils
import crawl
import uniq

from loaddb import query_do, query_first_col
from query import count_points, assign_points, assign_team_points, wrap_transaction
from query import log_temp_points, log_temp_team_points, get_points

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
  query.update_most_recent_character(c, player,
                                     game_character(mile),
                                     mile['time'])

  miletype = milestone_type(mile)
  if miletype == 'uniq' and not milestone_desc(mile).startswith('banished '):
    do_milestone_unique(c, mile)
  if miletype == 'rune':
    do_milestone_rune(c, mile)
  elif miletype == 'ghost':
    do_milestone_ghost(c, mile)

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
  """When the player gets a rune for the first time, they get ten points.
  After that, they get one point. This one is pretty simple."""
  # Check if this player already found this kind of rune. Remember the db
  # is already updated, so for the first rune the count will be 1.
  rune = loaddb.extract_rune(mile['milestone'])
  num_rune = query.player_count_runes(c, mile['name'], rune)
  rune_points = (30 + num_rune - 1) / num_rune
  assign_points(c, "rune:" + rune, mile['name'], rune_points)
#  if query.player_count_runes(c, mile['name'], rune) > 1:
#    # player_already_has_rune:
#    assign_points(c, "rune:" + rune, mile['name'], 1)
#  else:
#    # 50 points for the first time the player finds a rune.
#    assign_points(c, "rune_1st:" + rune, mile['name'], 50)
  player = mile['name']
  banner.safe_award_banner(c, player, 'tso', 3)
  if (not banner.player_has_banner(c, player, 'ashenzari')
      and query.player_count_distinct_runes(c, player) == crawl.NRUNES):
    banner.award_banner(c, player, 'ashenzari', 12)

def do_milestone_ghost(c, mile):
  """When you kill a player ghost, you get two clan points! Otherwise this
  isn't terribly remarkable."""
  if not mile['milestone'].startswith('banished'):
    assign_team_points(c, "ghost", mile['name'], 2)

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


def game_fruit_mask(g):
  return g.has_key('fruit') and int(g['fruit']) or 0


def check_fedhas_banner(c, g):
  fruit_mask = game_fruit_mask(g)
  if fruit_mask:
    player = game_player(g)
    full_fruit_mask = query.player_update_get_fruit_mask(c, player, fruit_mask)
    if crawl.fruit_basket_complete(full_fruit_mask):
      banner.safe_award_banner(c, player, 'fedhas', 5)

def crunch_misc(c, g):
  player = g['name']
  ktyp = g['ktyp']

  if ktyp != 'winning':
    query.kill_active_streak(c, player)

  check_fedhas_banner(c, g)

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

  if g.has_key('maxskills'):
    maxed_skills = g['maxskills'].split(",")
    for sk in maxed_skills:
      query.register_maxed_skill(c, player, sk)
  if g.has_key('fifteenskills'):
    fifteen_skills = g['fifteenskills'].split(",")
    for sk in fifteen_skills:
      if sk in crawl.MAGIC_SKILLS:
        query.register_fifteen_skill(c, player, sk)

def repeat_race_class(previous_chars, char):
  """Returns 0 if the game does not repeat a previous role or class, 1 if
  it repeats a role xor class, 2 if it repeats a role and a class."""
  repeats = 0
  if char[0:2] in [c[0:2] for c in previous_chars]:
    repeats += 1
  if char[2:] in [c[2:] for c in previous_chars]:
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

  # Award Orb banner for wins.
  banner.safe_award_banner(c, player, 'okawaru', 9)

  if not query.game_did_visit_lair(c, player, game_start_time(game)):
    # assign_points(c, 'lairless_win', player, 20)
    if not query.game_did_visit_branch(c, player, game_start_time(game)):
      # 40 bonus points for winning without doing any branches.
      assign_points(c, 'branchless_win', player, 40)
      # And the banner:
      banner.safe_award_banner(c, player, 'kikubaaqudgha', 8)

  debug("%s win (%s), runes: %d" % (player, charabbrev, game.get('urune') or 0))

  if is_all_runer(game):
    all_allruners = number_of_allruners_before(c, game)
    assign_points(c, "nth_all_rune_win:%d" % (all_allruners + 1),
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

  game_god = query.get_game_god(c, game)
  banner_god = game_god.lower().replace(' ', '_')

  # Assign 25 extra points for winning with a god that you haven't used before.
  if (not query.is_god_repeated(c, game['name'], game_god)
      and not game_god == 'faithless'):
    query.record_won_god(c, game['name'], game_god)
    assign_points(c, "win_god:" + banner_god, game['name'], 25)

  repeated = 0
  if n_my_wins > 0:
    repeated = repeat_race_class([x['charabbrev'] for x in my_wins],
                                 game['char'])

  if n_my_wins == 0:
    # First win! I bet you don't have a streak
    assign_points(c, "my_1st_win", game['name'], 100)

  elif n_my_wins == 1 and repeated == 0:
    # Second win! If neither repeated race or class, bonus!
    assign_points(c, "my_2nd_win_norep", game['name'], 50)

  else:
    # Any win gets 10 points at this point.
    assign_points(c, "my_win", game['name'], 10)

  streak_wins = query.wins_in_streak_before(c, game['name'], game_end)
  debug("%s win (%s), previous games in streak: %s" %
        (game['name'], game['char'], streak_wins))
  if not streak_wins:
    query.kill_active_streak(c, player)
    streak_len = -1
  else:
    # Award banner.
    banner.safe_award_banner(c, player, 'cheibriados', 9)
    # This length could be 1 even though it involves at least two games, beware!
    streak_len = compute_streak_length(streak_wins, game['char'])
    streak_species = 'streak_species:'+(game['char'][0:2])
    streak_class = 'streak_class:'+(game['char'][2:])
    # 75 points for streak games, but only if they are with a new race and class.
    assign_points(c, streak_species, game['name'], 50, False)
    assign_points(c, streak_class, game['name'], 25, False)
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
      banner.safe_award_banner(c, p, banner_name, prestige, temp)

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
    banner.award_banner(c, player, title, points, temp=True)

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
                    'max_streak_Nth:%d', [200, 100, 50])

  award_temp_trophy(c, pmap, query.get_top_unique_killers(c),
                    'top_uniq_killer:%d', [50, 20, 10])

#  award_temp_trophy(c, pmap, query.player_pacific_win_best(c),
#                    'top_pacific_win:%d', [200, 100, 50],
#                    team_points=True)

  # [snark] xl1 dive disabled for 2010 tourney.
  #award_temp_trophy(c, pmap, query.player_xl1_dive_best(c),
  #                  'xl1_dive_Nth:%d', [50, 20, 10],
  #                  team_points=True)

  award_temp_trophy(c, pmap, query.player_hs_combo_best(c),
                    'max_combo_hs_Nth:%d', [200, 100, 50],
                    can_share_places=True, team_points=True)

  award_temp_trophy(c, pmap, query.get_top_ziggurats(c),
                    'zig_rank:%d', [200, 100, 50], team_points=True)

  award_temp_trophy(c, pmap, query.player_rune_dive_best(c),
                    'rune_dive_rank:%d', [50, 20, 10], team_points=True)

  award_temp_trophy(c, pmap, query.player_deaths_to_uniques_best(c),
                    'deaths_to_uniques_Nth:%d', [50, 20, 10],
                    can_share_places=False,
                    team_points=True)

def check_banners(c):
  award_player_banners(c, 'lugonu',
                       query_first_col(c, '''SELECT DISTINCT player
                                             FROM atheist_wins'''),
                       9)
  award_player_banners(c, 'trog',
                       query_first_col(c, '''SELECT player
                                             FROM super_sigmund_kills'''),
                       1)
  award_player_banners(c, 'zin',
                       query_first_col(c, '''SELECT player
                                             FROM all_hellpan_kills'''),
                       6)
  award_player_banners(c, 'xom',
                       query_first_col(c,
                                       '''SELECT player FROM ziggy_players'''),
                       7)
  award_player_banners(c, 'jiyva',
                       query_first_col(c,
                                       '''SELECT player FROM ninenines_players'''),
                       7)
  award_player_banners(c, 'makhleb',
                       query_first_col(c,
                                       '''SELECT player FROM speed_demons'''),
                       7)
  award_player_banners(c, 'vehumet',
                       query_first_col(c,
                                       '''SELECT player FROM orbrun_runes'''),
                       7)
  award_player_banners(c, 'sif',
                       query_first_col(c,
                                       '''SELECT player FROM scholars'''),
                       7)

def check_misc_points(c, pmap):
  def award_misc_points(key, multiplier, rows):
    for r in rows:
      player = r[0]
      points = r[1] * multiplier
      record_points(pmap, player, points, team_points=False)
      log_temp_points(c, player, key % r[1], points)

  award_misc_points('combo_hs:%d', 5, query.all_hs_combos(c))
  award_misc_points('combo_hs_win:%d', 5, query.all_hs_combo_wins(c))
  award_misc_points('species_hs:%d', 20, query.all_hs_species(c))
  award_misc_points('class_hs:%d', 10, query.all_hs_classes(c))

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
