#!/usr/bin/python

import loaddb
import query
import banner

import logging
from logging import debug, info, warn, error
import crawl_utils
import uniq

from loaddb import query_do, query_first_col
from query import assign_points, assign_team_points
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

def act_on_milestone(c, this_mile):
  """This function takes a milestone line, which is a string composed of key/
  value pairs separated by colons, and parses it into a dictionary.
  Then, depending on what type of milestone it is (key "type"), another
  function may be called to finish the job on the milestone line. Milestones
  have the same broken :: behavior as logfile lines, yay."""
  if this_mile['type'] == 'unique' and \
        not this_mile['milestone'].startswith('banished '):
    do_milestone_unique(c, this_mile)
  if this_mile['type'] == 'rune':
    do_milestone_rune(c, this_mile)
  if this_mile['type'] == 'ghost':
    do_milestone_ghost(c, this_mile)

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
  if query.player_count_runes(c, mile['name'], rune) > 1:
    # player_already_has_rune:
    assign_points(c, "rune:" + rune, mile['name'], 1)
  else:
    # first time getting this rune!
    assign_points(c, "rune_1st:" + rune, mile['name'], 10)
  player = mile['name']
  banner.safe_award_banner(c, player, 'Rune')

def do_milestone_ghost(c, mile):
  """When you kill a player ghost, you get two clan points! Otherwise this
  isn't terribly remarkable."""
  assign_team_points(c, "ghost", mile['name'], 2)

def act_on_logfile_line(c, this_game):
  """Actually assign things and write to the db based on a logfile line
  coming through. All lines get written to the db; some will assign
  irrevocable points and those should be assigned immediately. Revocable
  points (high scores, lowest dungeon level, fastest wins) should be
  calculated elsewhere."""
  if this_game['ktyp'] == 'winning':
    crunch_winner(c, this_game) # lots of math to do for winners

  crunch_misc(c, this_game)

  if loaddb.is_ghost_kill(this_game):
    ghost = loaddb.extract_ghost_name(this_game['killer'])
    XL = this_game['xl']
    if XL > 5:
      assign_team_points(c, "gkill", ghost, (XL - 5))

def crunch_misc(c, g):
  ktyp = g['ktyp']

  def strip_unique_qualifier(x):
    if ',' in x:
      p = x.index(',')
      return x[:p]
    return x

  killer = strip_unique_qualifier(g.get('killer') or '')
  player = g['name']
  if uniq.is_uniq(killer):
    query_do(c,
             '''INSERT INTO deaths_to_uniques
                            (player, uniq, start_time, end_time)
                     VALUES (%s, %s, %s, %s)''',
             player, killer, g['start'], g['end'])

  if g.has_key('maxskills'):
    maxed_skills = g['maxskills'].split(",")
    for sk in maxed_skills:
      query.register_maxed_skill(c, player, sk)

def repeat_race_class(previous_chars, char):
  """Returns 0 if the game does not repeat a previous role or class, 1 if
  it repeats a role xor class, 2 if it repeats a role and a class."""
  repeats = 0
  if char[0:2] in [c[0:2] for c in previous_chars]:
    repeats += 1
  if char[2:] in [c[2:] for c in previous_chars]:
    repeats += 1
  return repeats

def is_god_repeated(previous_wins, g):
  """Returns true if the god in the current game was already used by
the player in a previous winning game. The gods checked are the gods
at end of game."""
  def god(g):
    return g.get('god') or ''
  return god(g) in [god(x) for x in previous_wins]

def crunch_winner(c, game):
  """A game that wins could assign a variety of irrevocable points for a
  variety of different things. This function needs to calculate them all."""

  debug("%s win (%s), runes: %d" % (game['name'], game['char'],
                                    game['urune']))

  if is_all_runer(game):
    all_allruners = number_of_allruners_before(c, game)
    assign_points(c, "nth_all_rune_win:%d" % (all_allruners + 1),
                  game['name'],
                  get_points(all_allruners, 200, 100, 50))

    # If this is my first all-rune win, 50 points!
    if query.count_wins(c, player = game['name'],
                        runes = query.MAX_RUNES,
                        before = game['end']) == 0:
      assign_points(c, "my_1st_all_rune_win", game['name'], 50)

  previous_wins = query.count_wins(c, before = game['end'])
  assign_points(c,
                "nth_win:%d" % (previous_wins + 1),
                game['name'], get_points(previous_wins, 200, 100, 50))

  my_wins = query.get_winning_games(c, player = game['name'],
                                    before = game['end'])
  n_my_wins = len(my_wins)

  # Assign 20 extra points for winning with a god that you haven't used before.
  if not is_god_repeated(my_wins, game) and not query.did_change_god(game):
    god = (game.get('god') or 'atheist').lower()
    query.record_won_god(c, player, game.get('god') or '')
    assign_points(c, "my_win_" + god, 20)

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

  # For one or more prior wins, check streaks
  if n_my_wins >= 1:
    # Check if this is a streak. streak_wins will be empty if not on
    # a streak.
    streak_wins = query.wins_in_streak_before(c, game['name'], game['end'])

    debug("%s win (%s), previous games in streak: %s" %
          (game['name'], game['char'], streak_wins))

    if streak_wins:
      streak_len = len(streak_wins) + 1
      # First update the streaks table. We're still in the logfile transaction
      # here, so it's safe.
      if streak_len > loaddb.longest_streak_count(c, game['name']):
        loaddb.update_streak_count(c, game, streak_len)

      streak_repeats = repeat_race_class(streak_wins, game['char'])

      # 100, 30, 10 points for streak games based on no repeat, xor, repeat.
      assign_points(c, "streak_win",
                    game['name'], get_points(streak_repeats, 100, 30, 10))

    # If this is a non-streak win, make sure we're not on the second
    # win with no repeats, since we've already done the bonus points
    # for that above.
    elif n_my_wins >= 2 or (n_my_wins == 1 and repeated == 1):
      assign_points(c, "my_nonstreak_norep",
                    game['name'], get_points(repeated, 30, 10))

def is_all_runer(game):
  """Did this game get every rune? This _might_ require checking the milestones
  associated with the start time..."""
  return game['urune'] == query.MAX_RUNES

def number_of_allruners_before(c, game):
  """How many all-runers happened before this game? We can stop at 3."""
  return query.count_wins(c, runes = query.MAX_RUNES, before = game['end'])

###################### Additional scoring math ##########################

def player_additional_score(c, player):
  """Calculates the player's total score, including unchanging score and the
  current volatile score."""

  additional = 0
  add_team = 0

  query.audit_flush_player(c, player)
  rt_pos = query.player_fastest_realtime_win_pos(c, player)
  additional += log_temp_points( c, player,
                                 'fastest_realtime:%d' % (rt_pos + 1),
                                 get_points(rt_pos, 200, 100, 50 ) )

  tc_pos = query.player_fastest_turn_win_pos(c, player)
  additional += log_temp_points( c, player,
                                 'fastest_turncount:%d' % (tc_pos + 1),
                                 get_points(tc_pos, 200, 100, 50 ) )

  combo_hs = query.count_hs_combos(c, player)
  additional += log_temp_points( c, player, 'combo_hs:%d' % combo_hs,
                                 combo_hs * 5 )

  combo_hs_win = query.count_hs_combo_wins(c, player)
  additional += log_temp_points( c, player, 'combo_hs_win:%d' % combo_hs_win,
                                 combo_hs_win * 5 )

  species_hs = query.count_hs_species(c, player)
  additional += log_temp_points( c, player, 'species_hs:%d' % species_hs,
                                 species_hs * 10 )

  class_hs = query.count_hs_classes(c, player)
  additional += log_temp_points( c, player, 'class_hs:%d' % class_hs,
                                 class_hs * 10 )

  combo_hs_pos = query.player_hs_combo_pos(c, player)
  additional += log_temp_points( c, player,
                                 'max_combo_hs_Nth:%d' % (combo_hs_pos + 1),
                                 get_points(combo_hs_pos, 200, 100, 50 ) )

  streak_pos = query.player_streak_pos(c, player)
  additional += log_temp_points( c, player,
                                 'max_streak_Nth:%d' % (streak_pos + 1),
                                 get_points(streak_pos, 200, 100, 50 ) )

  uniq_kill_pos = query.player_unique_kill_pos(c, player)
  addditional += log_temp_points( c, player,
                                  'top_uniq_killer:%d' % (uniq_kill_pos + 1),
                                  get_points(uniq_kill_pos, 50, 20, 10 ) )


  pacific_win_pos = query.player_pacific_win_pos(c, player)
  add_team += log_temp_team_points(c, player,
                                   ('top_pacific_win:%d'
                                    % (pacific_win_pos + 1)),
                                   get_points(pacific_win_pos, 200, 100, 50))

  xl1_dive_pos = query.player_xl1_dive_pos(c, player)
  add_team += log_temp_team_points( c, player,
                                    'xl1_dive_Nth:%d' % (xl1_dive_pos + 1),
                                    get_points(xl1_dive_pos, 50, 20, 10) )

  ziggurat_dive_pos = query.player_ziggurat_dive_pos(c, player)
  add_team += log_temp_team_points( c, player,
                                    'zig_rank:%d' % (ziggurat_dive_pos + 1),
                                    get_points(ziggurat_dive_pos,
                                               200, 100, 50))


  rune_dive_pos = query.player_rune_dive_pos(c, player)
  add_team += log_temp_team_points( c, player,
                                    'rune_dive_rank:%d' % (rune_dive_pos + 1),
                                    get_points(rune_dive_pos, 50, 20, 10) )

  most_deaths_to_uniques_pos = query.player_deaths_to_uniques_pos(c, player)
  add_team += log_temp_team_points( c, player,
                                    'deaths_to_uniques_Nth:%d'
                                    % (most_deaths_to_uniques_pos + 1),
                                    get_points(most_deaths_to_uniques_pos,
                                               50, 20, 10))

  loaddb.update_player_fullscore(c, player, additional, add_team)
  return additional

def update_player_scores(c):
  wrap_transaction(safe_update_player_scores)(c)

def award_player_banners(c, banner, players):
  if players:
    for p in players:
      banner.safe_award_banner(c, p, banner)

def safe_update_player_scores(c):
  for p in query.get_players(c):
    info("Updating full score for %s" % p)
    player_additional_score(c, p)

  # Award moose & squirrel banners.
  award_player_banners(c, 'Moose',
                       query_first_col(c, '''SELECT DISTINCT player
                                             FROM double_boris_kills'''))
  # Award 'Atheist' banners
  award_player_banners(c, 'Atheist,',
                       query_first_col(c, '''SELECT DISTINCT player
                                               FROM atheist_wins'''))

  # Award 'Scythe' banners
  award_player_banners(c, 'Scythe',
                       query_first_col(c, '''SELECT player
                                             FROM super_sigmund_kills'''))

  # Award 'Orb' banner for wins.
  award_player_banners(c, 'Orb',
                       query_first_col(c, '''SELECT DISTINCT player
                                               FROM games
                                              WHERE killertype='winning' '''))

  award_player_banners(c, 'Free Will',
                       query_first_col(c, '''SELECT DISTINCT player
                                             FROM free_will_wins'''))
  award_player_banners(c, 'Ghostbuster',
                       query_first_col(c,
                                       '''SELECT player FROM ghostbusters'''))

  award_player_banners(c, 'Shopaholic',
                       query_first_col(c,
                                       '''SELECT DISTINCT player
                                            FROM compulsive_shoppers'''))
