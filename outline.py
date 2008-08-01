#!/usr/bin/python

import loaddb
import query

import logging
from logging import debug, info, warn, error

from query import assign_points, assign_team_points, say_points, get_points

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

# Update player scores every 5 mins.
TIMER = [ ( 5 * 60, OutlineTimer() ) ]

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
  assign_points(c, "unique:" + unique, mile['name'], 5)

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

  if loaddb.is_ghost_kill(this_game):
    ghost = loaddb.extract_ghost_name(this_game['killer'])
    XL = this_game['xl']
    if XL > 5:
      assign_points(c, "gkill", ghost, (XL - 5))

def repeat_race_class(previous_chars, char):
  """Returns 0 if the game does not repeat a previous role or class, 1 if
  it repeats a role xor class, 2 if it repeats a role and a class."""
  repeats = 0
  if char[0:2] in [c[0:2] for c in previous_chars]:
    repeats += 1
  if char[2:] in [c[2:] for c in previous_chars]:
    repeats += 1
  return repeats

def crunch_winner(c, game):
  """A game that wins could assign a variety of irrevocable points for a
  variety of different things. This function needs to calculate them all."""

  debug("%s win (%s), runes: %d" % (game['name'], game['char'],
                                    game['urune']))

  if is_all_runer(game):
    all_allruners = number_of_allruners_before(c, game)
    assign_points(c, "Nth_all_rune_win", game['name'],
                  get_points(all_allruners, 200, 100, 50))

    # If this is my first all-rune win, 50 points!
    if query.count_wins(c, player = game['name'],
                        runes = query.MAX_RUNES,
                        before = game['end']) == 0:
      assign_points(c, "my_1st_all_rune_win", game['name'], 50)

  previous_wins = query.count_wins(c, before = game['end'])
  assign_points(c,
                "Nth_win",
                game['name'], get_points(previous_wins, 200, 100, 50))

  my_wins = query.get_wins(c, player = game['name'], before = game['end'])
  n_my_wins = len(my_wins)

  repeated = 0
  if n_my_wins > 0:
    repeated = repeat_race_class(my_wins, game['char'])

  if n_my_wins == 0:
    # First win! I bet you don't have a streak
    assign_points(c, "my_1st_win", game['name'], 100)

  elif n_my_wins == 1 and repeated == 0:
    # Second win! If neither repeated race or class, bonus!
    assign_points(c, "my_2nd_win_norep", game['name'], 50)

  else:
    # Any win gets 10 points at this point.
    assign_points(c, "my_boring_win", game['name'], 10)

  # For one or more prior wins, check streaks
  if n_my_wins >= 1:
    # Check if this is a streak. streak_wins will be empty if not on
    # a streak.
    streak_wins = query.wins_in_streak_before(c, game['name'], game['end'])

    debug("%s win (%s), previous games in streak: %s" %
          (game['name'], game['char'], streak_wins))

    if streak_wins:
      # First update the streaks table. We're still in the logfile transaction
      # here, so it's safe.
      loaddb.update_streak_count(c, game, len(streak_wins) + 1)

      streak_repeats = repeat_race_class(streak_wins, game['char'])

      # 100, 30, 10 points for streak games based on no repeat, xor, repeat.
      assign_points(c, "streak_win",
                    game['name'], get_points(streak_repeats, 100, 30, 10))

    # If this is a non-streak win, make sure we're not on the second win,
    # since we've already done the bonus points for that above.
    elif n_my_wins >= 2:
      assign_points(c, "my_nonstreak_norep",
                    game['name'], get_points(repeated, 30, 10))

def is_all_runer(game):
  """Did this game get every rune? This _might_ require checking the milestones
  associated with the start time..."""
  return game['urune'] == query.MAX_RUNES

def number_of_allruners_before(c, game):
  """How many all-runers happened before this game? We can stop at 3."""
  return query.count_wins(c, runes = query.MAX_RUNES, before = game['end'])

def whereis(player):
  """We might want to know where a player is, either to display it on the
  website or to... well, I can't think of another reason. This function
  will give us a string to put on the site at the top of a player page
  or something similar."""
  # This is basically all pulled out of Henzell. Thanks, Henzell!
  # It's much messier than what I've done so far, but I want to
  # avoid duplicating known-done work.
  rawdatapath = "/home/crawl/chroot/dgldir/ttyrec/"
  try:
    whereline = open(rawdatapath + '%s/%s.where' % (player, player)).readlines()[0][:-1]
  except IOError:
    return ("No whereis info for %s." % player)
  details = parse_logline(whereline)
  version = details['v']
  if ':' in details['place']:
    prep = 'on'
  else:
    prep = 'in'
  prestr = godstr = datestr = turnstr_suffix = turnstr = ''
  try:
    godstr = ', a worshipper of %s,' % details['god']
  except KeyError:
    godstr = ''
  try:
    month = str(int(details['time'][4:6]) + 1)
    if len(month) < 2:
      month = '0' + month
    datestr = ' on %s-%s-%s' % (details['time'][0:4], month,
                                details['time'][6:8])
  except KeyError:
    datestr = ''
  nturns = int(details['turn'])
  status = details['status']
  if int(details['turn']) != 1:
    turnstr_suffix = 's'
  turnstr = ' after %d turn%s' % (int(details['turn']), turnstr_suffix)
  if status == 'saved':
    prestr = 'last saved'
  elif status in [ 'dead', 'quit', 'won', 'bailed out' ]:
    return ("%s is currently dead." % (player))
    # This should be changed to say where they died, but the Henzell
    # way to do that calls a ruby script so I am going to write my own.
  elif status == 'active':
    prestr = 'is currently'
    datestr = ''
  sktitle = game_skill_title(details)
  if (status != 'won') and (status != 'bailed out'):
    return ("%s the %s (L%s %s)%s %s %s %s%s%s." % (player, sktitle, details['xl'], details['char'], godstr, prestr, prep, replace(details['place'], ';', ':'), datestr, turnstr))
  return ("Whereis information for %s is not currently available." % (player))


###################### Additional scoring math ##########################

def player_additional_score(c, player, update=True):
  """Calculates the player's total score, including unchanging score and the
  current volatile score."""

  additional = 0

  additional += say_points( player, 'fastest_realtime',
                            get_points(
                                query.player_fastest_realtime_win_pos(
                                      c, player),
                                200, 100, 50 ) )
  additional += say_points( player, 'fastest_turncount',
                            get_points(
                                query.player_fastest_turn_win_pos(c, player),
                                200, 100, 50 ) )
  additional += say_points( player, 'combo_hs',
                            query.count_hs_combos(c, player) * 5 )
  additional += say_points( player, 'combo_hs_win',
                            query.count_hs_combo_wins(c, player) * 5 )
  additional += say_points( player, 'species_hs',
                            query.count_hs_species(c, player) * 10 )
  additional += say_points( player, 'class_hs',
                            query.count_hs_classes(c, player) * 10 )
  additional += say_points( player, 'max_combo_hs',
                            get_points( query.player_hs_combo_pos(c, player),
                                        200, 100, 50 ) )
  additional += say_points( player, 'max_streak',
                            get_points( query.player_streak_pos(c, player),
                                        200, 100, 50 ) )

  if update:
    loaddb.update_player_fullscore(c, player, additional)

  return additional

def update_player_scores(c):
  for p in query.get_players(c):
    info("Updating full score for %s" % p)
    player_additional_score(c, p)
