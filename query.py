# Library to query the database and update scoring information. Raw data entry
# from logfile and milestones is done in loaddb.py, this is for queries and
# post-processing.

import logging
from logging import debug, info, warn, error

import loaddb
from loaddb import Query, query_do, query_first, query_row, query_rows
from loaddb import query_rows_with_ties
from loaddb import query_first_col, query_first_def

import combos
import crawl
import crawl_utils
import uniq
import os.path
import re
from datetime import datetime
import time

MAX_RUNES = 15

LOG_FIELDS = [ 'source_file' ] + [ x[1] for x in loaddb.LOG_DB_MAPPINGS ]

def _cursor():
  """Easy retrieve of cursor to make interactive testing easier."""
  d = loaddb.connect_db()
  return d.cursor()

def _filter_invalid_where(d):
  if loaddb.is_not_tourney(d):
    return None
  status = d['status']
  if status in [ 'quit', 'won', 'bailed out', 'dead' ]:
    return None
  else:
    d['status'] = status.title() or 'Active'
    return d

def time_from_str(when):
  if isinstance(when, datetime):
    return when
  if when.endswith('D') or when.endswith('S'):
    when = when[:-1]
  return datetime(*(time.strptime(when, '%Y%m%d%H%M%S')[0:6]))

def canonical_where_name(name):
  test = '%s/%s' % (crawl_utils.RAWDATA_PATH, name)
  if os.path.exists(test) or not os.path.exists(crawl_utils.RAWDATA_PATH):
    return name
  names = os.listdir(crawl_utils.RAWDATA_PATH)
  names = [ x for x in names if x.lower() == name.lower() ]
  if names:
    return names[0]
  else:
    return None

def game_is_over(c, name, start):
  query = Query('''SELECT COUNT(*) FROM games WHERE player=%s 
                                   AND start_time=%s''', name, start)
  return (query.count(c) > 0)

def whereis_player(c, name, src):
  mile = query_row(c, '''SELECT start_time, mile_time
                           FROM whereis_table
                          WHERE player = %s AND src = %s''', name, src)
  if not mile:
    return None
  last_game = query_row(c, '''SELECT start_time
                                FROM last_game_table
                               WHERE player = %s AND src = %s''', name, src)
  if last_game and last_game[0] >= mile[0]:
    return None
  return query_row(c, '''SELECT milestone_time, player, title, xl, charabbrev,
                                god, milestone, place, turn, duration
                           FROM milestones
                          WHERE player = %s
                            AND start_time = %s
                            AND milestone_time = %s''',
                   name, mile[0], mile[1])

def whereis_all_players(c):
  whereis_list = []
  rows = query_rows(c, '''SELECT player, src, start_time, mile_time
                            FROM whereis_table''')
  for r in rows:
    last_game = query_row(c, '''SELECT start_time
                                FROM last_game_table
                                WHERE player = %s AND src = %s''', r[0], r[1])
    if last_game and last_game[0] >= r[2]:
      continue
    mile = query_row(c, '''SELECT milestone_time, player, title, xl, charabbrev,
                                god, place, runes
                           FROM milestones
                          WHERE player = %s
                            AND start_time = %s
                            AND milestone_time = %s''',
                   r[0], r[2], r[3])
    whereis_list.append((r[1], mile))
  return whereis_list

def get_game_god(c, game):
  game_god = game.get('god') or 'No God'
  if (game_god == 'Xom' or game_god == 'No God') and not did_change_god(c, game):
    return game_god
  game_god = query_row(c,
                         '''SELECT noun FROM milestones
                            WHERE player = %s AND start_time = %s
                              AND verb = 'god.maxpiety'
                            ORDER BY milestone_time ASC''',
                         game['name'], game['start'])
  if game_god is None:
    return 'faithless'
  return game_god[0]

def did_change_god(c, game):
  """Returns true if the player changed gods during the game, by checking
  for a god.renounce milestone."""
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND (verb = 'god.renounce'
                            OR verb = 'god.worship') ''',
                      game['name'], game['start']) > 0)

def win_query(selected, order_by = None,
              player=None, charabbr=None, character_race=None, raceabbr=None,
              character_class=None, classabbr=None, runes=None,
              before=None, limit=None):

  table = 'games'
  query = Query("SELECT " + selected + " FROM " + table +
                " WHERE killertype='winning' ")
  if player:
    query.append(' AND player=%s', player)
  if (charabbr):
    query.append(' AND charabbrev=%s', charabbr)
  if (character_race):
    query.append(' AND race=%s', character_race)
  if (raceabbr):
    query.append(' AND MID(charabbrev,1,2) = %s', raceabbr)
  if (character_class):
    query.append(' AND class=%s', character_class)
  if (classabbr):
    query.append(' AND MID(charabbrev,3,2) = %s', classabbr)
  if (runes):
    query.append(' AND runes >= %s', runes)
  if before:
    query.append(' AND end_time < %s', before)
  if order_by:
    query.append(' ' + order_by)
  if limit:
    query.append(" LIMIT %d" % limit)
  return query

def first_win_for_combo(c, charabbrev, game_end):
  table = 'games'
  return query_first(c, "SELECT COUNT(*) FROM " + table +
                        """ WHERE killertype = 'winning' AND charabbrev = %s
                              AND end_time < %s""",
                     charabbrev, game_end) == 0

def get_player_won_gods(c, player):
  """Returns the names of all the gods that the player has won games with,
wins counting only if the player has not switched gods during the game."""
  return query_first_col(c,
                         "SELECT god FROM player_won_gods WHERE player = %s",
                         player)

def get_player_best_streak_games(c, player):
  streaks = query_row(c, '''SELECT streak_time
                            FROM streaks
                            WHERE player = %s''',
                      player)
  if streaks is None:
    return []

  return get_streak_games(c, player, streaks[0])

def player_top_scores(c, limit=5):
  return query_rows(c, '''SELECT player, score
                            FROM games
                        ORDER BY score DESC
                           LIMIT %d''' % limit)

def player_last_started_win(c):
  return query_rows(c, '''SELECT player, end_time FROM last_started_win''')

def player_hare_candidates(c):
  if loaddb.time_in_hare_window():
    return player_last_started_win(c)
  else:
    return []

def logfile_fields(prefix = None):
  if prefix:
    return ",".join([ prefix + x for x in LOG_FIELDS ])
  else:
    return ",".join(LOG_FIELDS)

def get_fastest_time_player_games(c):
  fields = logfile_fields('g.')
  games = query_rows(c, '''SELECT %s FROM fastest_realtime f, games g
                           WHERE f.id = g.id''' % fields)
  return [ row_to_xdict(r) for r in games ]

def get_fastest_time_allruner_player_games(c):
  fields = logfile_fields('g.')
  games = query_rows(c, '''SELECT %s FROM fastest_realtime_allruner f, games g
                           WHERE f.id = g.id''' % fields)
  return [ row_to_xdict(r) for r in games ]

def get_fastest_turn_player_games(c):
  fields = logfile_fields('g.')
  games = query_rows(c, '''SELECT %s FROM fastest_turncount f, games g
                           WHERE f.id = g.id''' % fields)
  return [ row_to_xdict(r) for r in games ]

def get_top_streaks_from(c, table, min_streak, how_many,
                         add_next_game=False):
  streaks = query_rows(c, '''SELECT player, streak, streak_time
                             FROM %s
                             WHERE streak >= %s
                             ORDER BY streak DESC, streak_time
                             LIMIT %d''' % (table, '%s', how_many),
                       min_streak)
  # Convert tuples to lists.
  streaks = [ list(x) for x in streaks ]
  # And the fourth item in each row has to be a list of the streak games.
  # And haha, you thought this was easy? :P
  for streak in streaks:
    streak.append( get_streak_games(c, streak[0], streak[2]) )
    if add_next_game:
      streak.append(
        find_most_recent_character_since(c, streak[0]) or '?')
  return streaks

def get_top_active_streaks(c, how_many = 10):
  return get_top_streaks_from(c, 'active_streaks', 2, how_many,
                              add_next_game=True)

def get_top_streaks(c, how_many = 3):
  return get_top_streaks_from(c, 'streaks', 2, how_many)

def get_top_clan_scores(c, how_many=10):
  return query_rows_with_ties(c, '''SELECT name, owner, total_score
                           FROM teams
                           WHERE total_score > 0''',
                           'total_score', how_many, 2)

def get_top_clan_unique_kills(c, how_many=3):
  return query_rows(c, '''SELECT c.name, u.team_captain, u.kills, u.end_time
                          FROM teams c, clan_unique_kills u
                          WHERE c.owner = u.team_captain
                            AND u.kills > 0
                          ORDER BY u.kills DESC, u.end_time
                          LIMIT %d''' % how_many)

def get_top_clan_combos(c, how_many = 3):
  return query_rows_with_ties(c, '''SELECT c.name, hs.team_captain, hs.combos
                          FROM teams c, combo_hs_clan_scoreboard hs
                          WHERE c.owner = hs.team_captain''',
                          'hs.combos', how_many, 2)

def get_combo_scores(c, how_many=None, player=None):
  query = Query("SELECT " + ",".join(LOG_FIELDS) +
                (""" FROM combo_highscores
                       %s
                     ORDER BY score DESC, charabbrev""" %
                 (player and 'WHERE player = %s' or '')))
  if player is not None:
    query.vappend(player)
  if how_many:
    query.append(" LIMIT %d" % how_many)
  return [ row_to_xdict(x) for x in query.rows(c) ]

def get_clan_combo_scores(c, how_many=None, captain=None):
  query = Query("SELECT team_captain, " + ",".join(LOG_FIELDS) +
                (""" FROM clan_combo_highscores
                       %s
                     ORDER BY score DESC, charabbrev""" %
                 (captain and 'WHERE team_captain = %s' or '')))
  if captain is not None:
    query.vappend(captain)
  if how_many:
    query.append(" LIMIT %d" % how_many)
  return [ [x[0], row_to_xdict(x[1:])] for x in query.rows(c) ]

def get_species_scores(c, how_many=None, player=None):
  query = Query("SELECT " + ",".join(LOG_FIELDS) +
                (""" FROM species_highscores
                       %s
                     ORDER BY score DESC, race""" %
                 (player and 'WHERE player = %s' or '')))
  if player is not None:
    query.vappend(player)
  if how_many:
    query.append(" LIMIT %d" % how_many)
  return [ row_to_xdict(x) for x in query.rows(c) ]

def get_class_scores(c, how_many=None, player=None):
  query = Query("SELECT " + ",".join(LOG_FIELDS) +
                (""" FROM class_highscores
                       %s
                     ORDER BY score DESC, class""" %
                 (player and 'WHERE player = %s' or '')))
  if player is not None:
    query.vappend(player)
  if how_many:
    query.append(" LIMIT %d" % how_many)
  return [ row_to_xdict(x) for x in query.rows(c) ]

def get_gkills(c):
  rows = query_rows(c,
                    """SELECT killer, COUNT(*) kills
                       FROM games
                       WHERE kgroup='player ghost'
                       GROUP BY killer
                       ORDER BY kills DESC""")
  if len(rows) > 50:
    rows = [ list(r) for r in rows if r[1] >= rows[49][1] ]
  else:
    rows = [ list(r) for r in rows ]
  for r in rows:
    ghost = r[0]
    victims = query_rows(c,
                         """SELECT player, COUNT(*) ntimes FROM games
                            WHERE killer = %s
                            GROUP BY player
                            ORDER BY ntimes DESC""",
                         ghost)
    r.append(victims)
  return rows

def get_death_causes(c):
  rows = query_rows(c,
                    """SELECT g.kgroup, g.killertype, COUNT(*) killcount,
                              (SELECT player FROM games
                               WHERE kgroup = g.kgroup
                               ORDER BY end_time DESC
                               LIMIT 1) latest
                       FROM games g
                       WHERE g.killertype NOT IN ('winning',
                                                  'quitting',
                                                  'leaving')
                       GROUP BY g.kgroup, g.killertype""")

  # Now to fix up the rows.
  clean_rows = [ ]
  last = None

  total = 0
  for r in rows:
    killer = r[0]
    total += r[2]
    if last and last[0] == killer:
      if r[1] == 'mon':
        kills_breakdown[0] += r[2]
      else:
        kills_breakdown[1] += r[2]
      clean_rows.pop()
      if kills_breakdown[0] > 0 and kills_breakdown[1] > 0:
        killer = "%s (%d melee, %d ranged)" % (killer, kills_breakdown[0], kills_breakdown[1])
      clean_rows.append( [ killer, kills_breakdown[0]+kills_breakdown[1], r[3] ] )
    else:
      if r[1] == 'mon':
        kills_breakdown = [ r[2], 0 ]
      else:
        kills_breakdown = [ 0, r[2] ]
      clean_rows.append( [ killer, r[2], r[3] ] )
    last = r

  clean_rows.sort(lambda a,b: int(b[1] - a[1]))

  r_art = re.compile(r'^an? ')

  for r in clean_rows:
    r[0] = r_art.sub('', r[0])
    r[2] = crawl_utils.linked_text(r[2], crawl_utils.player_link)
    r.insert(1, "%.2f%%" % calc_perc(r[1], total))

  return clean_rows

def _canonicalize_player_name(c, player):
  row = query_row(c, '''SELECT name FROM players WHERE name = %s''',
                  player)
  if row:
    return row[0]
  return None

canonicalize_player_name = \
    crawl_utils.Memoizer(_canonicalize_player_name, lambda args: args[1:])

def player_get_fruit_mask(c, player):
  return query_first(c, '''SELECT fruit_mask FROM players WHERE name = %s''',
                     player)

def player_update_get_fruit_mask(c, player, fruit_mask):
  """Updates the player's fruit mask and returns the new fruit mask."""
  query_do(c, '''UPDATE players SET fruit_mask = fruit_mask | %s
                  WHERE name = %s''', fruit_mask, player)
  return player_get_fruit_mask(c, player)

def player_fruit_found(c, player):
  """Returns a tuple with a list of fruits the player has found and the list
  of fruits the player has yet to find. Both lists are sorted alphabetically."""
  fruit_mask = player_get_fruit_mask(c, player)
  fruit_found = crawl.fruit_mask_to_fruits(fruit_mask)
  fruit_found_set = set(fruit_found)
  fruit_unfound = [x for x in crawl.FRUITS if x not in fruit_found_set]
  return (fruit_found, fruit_unfound)

def get_top_players(c, how_many=10):
   return query_rows_with_ties(c,
                         '''SELECT name, score_full FROM players
                             WHERE score_full > 0''',
                             'score_full', how_many, 1)

def get_top_unique_killers(c, how_many=3):
  return query_rows(c,
                    '''SELECT player, nuniques, kill_time FROM kunique_times
                       ORDER BY nuniques DESC, kill_time
                       LIMIT %d''' % how_many)

def get_top_combo_highscorers(c, how_many=3):
  return query_rows_with_ties(c,
                    '''SELECT player, nscores FROM combo_hs_scoreboard
                        WHERE nscores > 0''',
                        'nscores', how_many, 1)

def get_deepest_xl1_games(c, how_many=3):
  return find_games(c, xl = 1, sort_max = 'lvl', limit = how_many)

def most_pacific_wins(c, how_many=3):
  fields = ",".join(['g.' + x for x in LOG_FIELDS])
  rows = query_rows(c,
                    "SELECT " + fields + " FROM " +
                    ''' most_pacific_wins m, games g
                       WHERE m.id = g.id''')
  games = [ row_to_xdict(x) for x in rows ]
  return games

def find_monotonic_games(games):
  """Given a list of game dictionaries in chronological order by
  end_time, walks backwards from the end and returns the longest list
  such that each game's end_time <= the start time of the next game
  in the sequence."""
  reverse_chrono_list = list(games)
  reverse_chrono_list.reverse()
  reverse_filtered_list = []
  last_game = None
  for g in reverse_chrono_list:
    if last_game and g['end_time'] > last_game['start_time']:
      break
    last_game = g
    reverse_filtered_list.append(g)
  reverse_filtered_list.reverse()
  return reverse_filtered_list

def get_streak_games(c, player, end_time):
  """Returns the games in the player's streak of wins with the last game in
  the streak specified by the provided end_time. Streak times must be
  monotonically increasing; each game's end-time must be <= the next game's
  start time. Monotonicity will be checked from the most recent game backwards.
  Streak games are returned in chronological order."""
  q = Query('SELECT ' + ",".join(LOG_FIELDS) + ' FROM games ' +
            '''WHERE player = %s
               AND killertype = 'winning'
               AND end_time >
                     COALESCE((SELECT MAX(end_time) FROM games
                               WHERE player = %s
                               AND end_time < %s
                               AND killertype != 'winning'), DATE('19700101'))
               AND end_time <= %s
               ORDER BY end_time''',
            player, player, end_time, end_time)
  return find_monotonic_games([ row_to_xdict(x) for x in q.rows(c) ])

def wins_in_streak_before(c, player, before):
  """Returns all the wins in the streak before the given game. Caller
  must ensure that there actually are wins before this game!"""
  streak_games = get_streak_games(c, player, before)
  return [ x['charabbrev'] for x in streak_games[0 : -1] ]

def count_wins(c, **selectors):
  """Return the number wins recorded for the given player, optionally with
     a specific race, class, minimum number of runes, or any combination"""
  return win_query('COUNT(start_time)', **selectors).count(c)

def get_wins(c, **selectors):
  """Returns the charabbrevs for wins matching the provided criteria,
  ordered with earlier wins first."""
  return [ x[0] for x in
           win_query('charabbrev', order_by = 'ORDER BY end_time',
                     **selectors).rows(c) ]

def won_unwon_combos_with_games(cu, won_games):
  won_combos = set([x['charabbrev'] for x in won_games])
  combo_lookup = dict([(x['charabbrev'], x) for x in won_games])

  def game_charabbrev_link(count, g):
    if count > 1:
      return crawl_utils.linked_text(g, crawl_utils.morgue_link, 
                   "%s(%d)" % (g['charabbrev'], count))
    return crawl_utils.linked_text(g, crawl_utils.morgue_link, 
                   g['charabbrev'])

  won_combo_list = [game_charabbrev_link(count_wins(cu, charabbr=c), combo_lookup[c])
                    for c in combos.VALID_COMBOS
                    if c in won_combos]

  unwon_combo_list = [c for c in combos.VALID_COMBOS if c not in won_combos]

  return (won_combo_list, unwon_combo_list)

def won_unwon_combos(c):
  won_games = get_winning_games(c)
  return won_unwon_combos_with_games(c, won_games)

def get_winning_games(c, **selectors):
  """Returns the games for wins matching the provided criteria, ordered
  with earlier wins first. Exactly the same as get_wins, but returns
  the xlog dictionaries instead of the charabbrev"""
  if not selectors.has_key('limit'):
    selectors['limit'] = None
  return find_games(c, sort_max='end_time',
                    killertype='winning', **selectors)

def race_formula(total, subtotal):
  return (2*(48+total)+1+subtotal)/(2+subtotal)

def class_formula(total, subtotal):
  return (56+total+1+subtotal)/(2+subtotal)

def player_race_wins(c, name):
  return query_rows(c, """SELECT DISTINCT MID(charabbrev,1,2) FROM
       games WHERE killertype='winning' AND player=%s""", name)

def player_class_wins(c, name):
  return query_rows(c, """SELECT DISTINCT MID(charabbrev,3,2) FROM
       games WHERE killertype='winning' AND player=%s""", name)

def clan_race_wins(c, captain):
  return query_rows(c, """SELECT DISTINCT MID(g.charabbrev,1,2)
                          FROM games g, players p
                          WHERE g.killertype='winning' AND g.player = p.name
                          AND p.team_captain = %s""", captain)

def clan_class_wins(c, captain):
  return query_rows(c, """SELECT DISTINCT MID(g.charabbrev,3,2)
                          FROM games g, players p
                          WHERE g.killertype='winning' AND g.player = p.name
                          AND p.team_captain = %s""", captain)

def clan_max_points(c, captain, key):
  points = query_row(c,
                     '''SELECT pp.player, SUM(pp.points) total
                        FROM player_points pp, players p
                        WHERE pp.point_source = %s
                        AND pp.player = p.name
                        AND p.team_captain = %s
                        GROUP BY pp.player
                        ORDER BY total DESC''', key, captain)
  if points == None:
    return 0
  return points[1]

def player_specific_points(c, name):
  points = 0
  for g in player_race_wins(c, name):
    points += count_points(c, name, 'species_win:'+g[0])
  for g in player_class_wins(c, name):
    points += count_points(c, name, 'class_win:'+g[0])
  return points

def row_to_xdict(row):
  return dict( zip(LOG_FIELDS, row) )

def find_clan_games(c, captain, sort_min=None, sort_max=None, limit=1,
                    **dictionary):
  if sort_min is None and sort_max is None:
    sort_min = 'end_time'

  query = Query('SELECT ' + ",".join(LOG_FIELDS) + ' FROM games g, players p ' +
                '''WHERE g.player = p.name
                   AND p.team_captain = %s''',
                captain)
  for key, value in dictionary.items():
    query.append(' AND ' + key + ' = %s', value)

  if sort_min:
    query.append(' ORDER BY ' + sort_min)
  elif sort_max:
    query.append(' ORDER BY ' + sort_max + ' DESC')

  if limit:
    query.append(' LIMIT %d' % limit)

  return [ row_to_xdict(x) for x in query.rows(c) ]

def find_games(c, sort_min=None, sort_max=None, limit=1, **dictionary):
  """Finds all games matching the supplied criteria, all criteria ANDed
  together."""

  if sort_min is None and sort_max is None:
    sort_min = 'end_time'

  table = 'games'

  query = Query('SELECT ' + ",".join(LOG_FIELDS) + ' FROM ' + table)
  where = []
  values = []

  def append_where(where, clause, *newvalues):
    where.append(clause)
    for v in newvalues:
      values.append(v)

  for key, value in dictionary.items():
    if key == 'before':
      append_where(where, "end_time < %s", value)
    else:
      append_where(where, key + " = %s", value)

  order_by = ''
  if sort_min:
    order_by += ' ORDER BY ' + sort_min
  elif sort_max:
    order_by += ' ORDER BY ' + sort_max + ' DESC'

  if where:
    query.append(' WHERE ' + ' AND '.join(where), *values)

  if order_by:
    query.append(order_by)

  if limit:
    query.append(' LIMIT %d' % limit)

  return [ row_to_xdict(x) for x in query.rows(c) ]

def was_last_game_win(c, player):
  """Return a tuple (race, class) of the last game if the last game the player played was a win.  The "last
     game" is a game such that it has the greatest start time <em>and</em>
     greatest end time for that player (this is to prevent using multiple servers
     to cheese streaks.  If the last game was not a win, return None"""

  last_start_query = \
      Query('''SELECT start_time, end_time FROM games WHERE player=%s
               ORDER BY start_time DESC LIMIT 1;''',
            player)

  win_end_query = \
      Query('''SELECT start_time, end_time, race, class FROM games
               WHERE killertype='winning' AND player=%s
	       ORDER BY end_time DESC LIMIT 1;''',
            player)

  res = win_end_query.row(c)
  if res is None:
    return None

  win_start, win_end, race, character_class = res

  # we've got to have some results, the player won. This is just their
  # last start
  recent_start, recent_end = last_start_query.row(c)
  if recent_start == win_start and recent_end == win_end:
    return race, character_class
  else:
    return None

def num_uniques_killed(c, player):
  """Return the number of uniques the player has ever killed"""
  query = Query('''SELECT COUNT(DISTINCT monster) FROM kills_of_uniques
                   WHERE player=%s;''',
                player)
  return query.count(c)

def was_unique_killed(c, player, monster):
  """Return whether the player killed the given unique"""
  query = Query('''SELECT monster FROM kills_of_uniques
                   WHERE player=%s AND monster=%s LIMIT 1;''',
                player, monster)
  return query.row(c) is not None

def calc_perc(num, den):
  if den <= 0:
    return 0.0
  else:
    return num * 100.0 / den

def get_all_game_stats(c):
  played = query_first(c, '''SELECT COUNT(*) FROM games''')
  distinct_players = query_first(c, '''SELECT COUNT(DISTINCT player) FROM games''')
  won = query_first(c, """SELECT COUNT(*) FROM games
                          WHERE killertype='winning'""")
  distinct_winners = query_first(c, """SELECT COUNT(DISTINCT player) FROM games
                                       WHERE killertype='winning'""")
  win_perc = "%.2f%%" % calc_perc(won, played)
  played_text = "%d (%d players)" % (played, distinct_players)
  won_text = "%d (%d players)" % (won, distinct_winners)
  return { 'played' : played_text,
           'won' : won_text,
           'win_perc' : win_perc }

def get_all_player_stats(c):
  q = Query('''SELECT p.name, p.team_captain, t.name, p.score_full,
                      (SELECT COUNT(*) FROM games
                       WHERE player = p.name
                       AND killertype = 'winning') wincount,
                      (SELECT COUNT(*) FROM games
                       WHERE player = p.name) playcount
               FROM players p LEFT JOIN teams t
               ON p.team_captain = t.owner
               ORDER BY p.score_full DESC''')
  rows = [ list(r) for r in q.rows(c) ]
  clean_rows = [ ]
  for r in rows:
    captain = r[1]
    r = r[0:1] + r[2:]
    if captain is None:
      r[1] = ''
    else:
      r[1] = crawl_utils.linked_text(captain, crawl_utils.clan_link, r[1])
    r.append( "%.2f%%" % calc_perc( r[3], r[4] ) )
    clean_rows.append(r)
  return clean_rows

def get_clan_stats(c, captain):
  stats = { }
  points = query_row(c, '''SELECT total_score FROM teams
                           WHERE owner = %s''',
                     captain)
  if points is not None:
    stats['points'] = points[0]

  stats['won'] = query_first(c, '''SELECT COUNT(*) FROM games g, players p
                                   WHERE p.name = g.player
                                   AND killertype = 'winning'
                                   AND p.team_captain = %s''',
                             captain)
  stats['played'] = query_first(c, '''SELECT COUNT(*) FROM games g, players p
                                       WHERE p.name = g.player
                                       AND p.team_captain = %s''',
                                 captain)
  stats['win_perc' ] = "%.2f%%" % calc_perc(stats['won'], stats['played'])
  return stats

def get_player_stats(c, name):
  """Returns a dictionary of miscellaneous stats for the player."""
  points = query_row(c, '''SELECT score_full, team_score_full
                           FROM players WHERE name = %s''',
                     name)
  if points is None:
    return { }

  stats = { }
  stats['points'] = points[0]
  stats['team_points'] = points[1]

  # Get win/played stats.
  stats['won'] = \
      query_first(c,
                  """SELECT COUNT(*) FROM games
                     WHERE player = %s AND killertype = 'winning'""",
                  name)

  stats['played'] = \
      query_first(c,
                  """SELECT COUNT(*) FROM games WHERE player = %s""",
                  name)

  stats['win_perc'] = "%.2f%%" % calc_perc(stats['won'], stats['played'])
  return stats

def get_player_base_score(c, name):
  """Return the unchanging part of a player's score"""
  query = Query("""SELECT score_base FROM players WHERE name=%s;""",
                name)
  return query.first(c, "Player not found: %s" % name)

def get_player_base_team_score(c, name):
  """Return the unchanging part of a player's team score contribution"""
  query = Query("""SELECT team_score_base FROM players WHERE name=%s;""",
                name)
  return query.first(c, "Player not found: %s" % name)

def get_players(c):
  return [r[0] for r in
          query_rows(c, 'SELECT name FROM players')]

def get_clans(c):
  return [r[0] for r in query_rows(c, 'SELECT owner FROM teams')]

def say_points(who, what, points):
  if points > 0:
    debug("%s: ADD %d points [%s]" % (who, points, what))
  return points

def is_god_repeated(c, player, god):
  """Returns true if the player has already won a game with the
  specified god."""
  return query_first_def(c, False,
                         '''SELECT COUNT(*) FROM player_won_gods
                             WHERE player = %s AND COALESCE(god, '') = %s''',
                         player, god)

def record_won_god(c, player, god):
  query_do(c, "INSERT INTO player_won_gods VALUES (%s, %s)", player, god)

def audit_trail_player_points(c, player):
  """Gets the audit trail for the points assigned to the player."""
  return query_rows(c,
                    '''SELECT temp, point_source, SUM(points) total, COUNT(*) n
                    FROM player_points
                    WHERE player=%s AND points > 0
                    GROUP BY temp, point_source
                    ORDER BY temp, total DESC, n DESC, point_source''',
                    player)

def audit_trail_player_team_points(c, player):
  return query_rows(c,
                    '''SELECT temp, point_source, SUM(team_points) total,
                          COUNT(*) n
                       FROM player_points
                       WHERE player=%s AND team_points > 0
                       GROUP BY temp, point_source
                       ORDER BY temp, total DESC, n DESC, point_source''',
                    player)

def audit_clan_player_points(c, captain):
  """Gets the total points contributed to a clan by each player in the clan."""
  return query_rows(c,
                    '''SELECT name, (score_full + team_score_full) points
                       FROM players
                       WHERE team_captain = %s
                       ORDER BY points DESC, name''',
                    captain)

def audit_adjusted_clan_player_points(c, captain):
  return query_rows(c,
                    '''SELECT name, (score_full + team_score_full 
                                - player_score_only) points
                       FROM players
                       WHERE team_captain = %s
                       ORDER BY points DESC, name''',
                    captain)

def audit_clan_points(c, captain):
  return query_rows(c,
                    '''SELECT point_source, SUM(points) p
                       FROM clan_points
                       WHERE captain = %s
                       GROUP BY point_source
                       ORDER BY p DESC, point_source''',
                    captain)

def audit_record_points(c, who, what, points, temp, credited='points'):
  if points > 0:
    # Update the audit table.
    query_do(c, 'INSERT INTO player_points (player, temp, ' + credited + ',' +
                '''                         point_source)
                   VALUES (%s, %s, %s, %s)''',
             who, temp and 1 or 0, points, what)

def clan_audit_record_points(c, captain, what, points):
  if points > 0:
    query_do(c, '''INSERT INTO clan_points (captain, points, point_source)
                   VALUES (%s, %s, %s)''',
             captain, points, what)

def audit_flush_player(c):
  """Discards temporary points assigned to players from the audit table."""
  query_do(c, '''DELETE FROM player_points
                 WHERE temp = 1''')

def audit_flush_clan(c, captain):
  query_do(c, '''DELETE FROM clan_points WHERE captain = %s''', captain)

def log_temp_points(c, who, what, points):
  """Assign provisional points to a player."""
  if points > 0:
    say_points(who, what, points)
    audit_record_points(c, who, what, points, True)
  return points

def log_temp_team_points(c, who, what, points):
  """Assign provisional team points to a player. Team points are added only
  to the player's team, not to the player's individual score, but they
  still 'belong' to the player."""
  if points > 0:
    say_points(who + '(c)', what, points)
    audit_record_points(c, who, what, points, True, credited = 'team_points')
  return points

def log_temp_clan_points(c, captain, what, points):
  """Assign provisional clan points to the clan, given the captain of the clan.
  Clan points belong to the clan as a whole, not to any of the individual
  players. Clan points are always provisional, since the players in a clan
  are free to leave/rejoin at any time."""
  if points > 0:
    say_points('CLAN:' + captain, what, points)
    clan_audit_record_points(c, captain, what, points)
  return points

def get_points(index, *points):
  if index >= 0 and index < len(points):
    return points[index];
  return 0

def count_points(cursor, name, point_source):
  total = query_first(cursor,
                      '''SELECT SUM(points) FROM player_points
                         WHERE player = %s AND point_source = %s''',
                      name, point_source)
  if total is None:
    return 0
  return total

def assign_points(cursor, point_source, name, points, add=True):
  """Add points to a player's points in the db"""
  if add:
    new_points = points
  else:
    new_points = points - count_points(cursor, name, point_source)
  if new_points > 0:
    debug("%s: %d points [%s]" % (name, new_points, point_source))
    audit_record_points(cursor, name, point_source, new_points, False)
    query_do(cursor,
             """UPDATE players
                SET score_base = score_base + %s
                WHERE name = %s""",
             new_points, name)

def assign_team_points(cursor, point_source, name, points):
  """Add points to a players team in the db.  The name refers to the player, not the team"""
  if points > 0:
    debug("TEAM %s: %d points [%s]" % (name, points, point_source))
    audit_record_points(cursor, name, point_source, points, False,
                        credited = 'team_points')
    query_do(cursor,
             """UPDATE players
                SET team_score_base = team_score_base + %s
                WHERE name=%s;""",
             points, name)

def set_clan_points(c, captain, points):
  debug("TEAM %s: additional points = %d" % (captain, points))
  query_do(c, '''UPDATE teams
                 SET total_score =
                    (SELECT score FROM clan_total_scores
                     WHERE team_captain = %s) + %s
                 WHERE owner = %s''',
           captain, points, captain)

def count_player_unique_kills(cursor, player, unique):
  return query_first(cursor,
                     '''SELECT COUNT(*) FROM kills_of_uniques
                     WHERE player=%s AND monster=%s''',
                     player, unique)

def player_count_distinct_runes(c, player):
  return query_first(c, '''SELECT COUNT(DISTINCT rune)
                             FROM rune_finds
                            WHERE player = %s''',
                     player)

def player_count_runes(cursor, player, rune=None):
  """Counts the number of times the player has found runes (or a specific
  rune."""
  q = Query('''SELECT COUNT(rune) FROM rune_finds
               WHERE player = %s''', player)
  if rune:
    q.append(' AND rune = %s', rune)

  return q.first(cursor)

def player_count_br_enter(cursor, player, br=None):
  """Counts the number of times the player has entered branches (or a specific
  branch."""
  q = Query('''SELECT COUNT(br) FROM branch_enters
               WHERE player = %s''', player)
  if br:
    q.append(' AND br = %s', br)

  return q.first(cursor)

def player_count_br_end(cursor, player, br=None):
  """Counts the number of times the player has entered branches (or a specific
  branch."""
  q = Query('''SELECT COUNT(br) FROM branch_ends
               WHERE player = %s''', player)
  if br:
    q.append(' AND br = %s', br)

  return q.first(cursor)

def find_place(rows, player):
  """Given a list of one-tuple rows, returns the index at which the given
  player name occurs in the one-tuples, or -1 if the player name is not
  present in the list."""
  if rows is None:
    return -1
  p = [r[0] for r in rows]
  if player in p:
    return p.index(player)
  else:
    return -1

def do_place_numeric(rows, callfn):
  index = -1
  rindex = -1
  last_num = None
  for r in rows:
    rindex += 1
    if last_num != r[1]:
      index = rindex
    last_num = r[1]
    if not callfn(r, index):
      break

def find_place_numeric(rows, player):
  """Given a list of two-tuple rows, returns the index at which the given
  player name occurs in the two-tuples, or -1 if the player name is not
  present in the list. The second element of each tuple is considered to be
  a score. If any element has the same score as a preceding element, it is
  treated as being at the same index."""
  index = -1
  rindex = -1
  last_num = None
  for r in rows:
    rindex += 1
    if last_num != r[1]:
      index = rindex
    last_num = r[1]
    if r[0] == player:
      return index
  return -1

def player_fastest_realtime_win_best(c):
  return query_rows(c, 'SELECT player FROM fastest_realtime')

def player_fastest_realtime_allruner_win_best(c):
  return query_rows(c, 'SELECT player FROM fastest_realtime_allruner')

def player_fastest_realtime_win_pos(c, player):
  return find_place(player_fastest_realtime_win_best(c), player)

def player_fastest_realtime_allruner_win_pos(c, player):
  return find_place(player_fastest_realtime_allruner_win_best(c), player)

def player_fastest_turn_win_best(c):
  return query_rows(c, 'SELECT player FROM fastest_turncount')

def player_fastest_turn_win_pos(c, player):
  return find_place(player_fastest_turn_win_best(c), player)

def player_hs_combo_best(c):
  return query_rows(c, 'SELECT player, nscores FROM combo_hs_scoreboard')

def player_hs_combo_pos(c, player):
  return find_place_numeric(player_hs_combo_best(c), player)

def player_streak_best(c):
  return query_rows(c, 'SELECT player, streak FROM streak_scoreboard')

def player_streak_pos(c, player):
  return find_place(player_streak_best(c), player)

def player_unique_kill_pos(c, player):
  return find_place(
    query_rows(c, '''SELECT player FROM kunique_times
                   ORDER BY nuniques DESC, kill_time
                      LIMIT 3'''),
    player)

def player_pacific_win_best(c):
  return query_rows(c, '''SELECT player FROM most_pacific_wins''')

def player_pacific_win_pos(c, player):
  return find_place(player_pacific_win_best(c), player)

def player_uniques_killed(c, player):
  rows = query_rows(c, '''SELECT DISTINCT monster FROM kills_of_uniques
                          WHERE player = %s ORDER BY monster''',
                    player)
  return [ row[0] for row in rows ]

def uniques_unkilled(uniques_killed):
  killset = set(uniques_killed)
  return [ u for u in uniq.UNIQUES if u not in killset ]

def player_xl1_dive_best(c):
  return [ [g['player']] for g in get_deepest_xl1_games(c) ]

def player_xl1_dive_pos(c, player):
  return find_place(player_xl1_dive_best(c), player)

def clan_combo_pos(c, owner):
  return find_place_numeric(
    query_rows(c,
               '''SELECT team_captain, combos FROM
                         combo_hs_clan_scoreboard'''),
    owner)

def clan_unique_pos(c, owner):
  return find_place(
    query_rows(c,
               '''SELECT team_captain, kills FROM
                         clan_unique_kills
                   WHERE kills > 0'''),
    owner)

def all_hs_combos(c):
  return query_rows(c,
                     '''SELECT player, COUNT(*) FROM combo_highscores
                        GROUP BY player''')

def all_hs_combo_wins(c):
  return query_rows(c,
                     '''SELECT player, COUNT(*) FROM game_combo_win_highscores
                        GROUP BY player''')

def all_hs_species(c):
  return query_rows(c,
                    '''SELECT player, COUNT(*) FROM species_highscores
                       GROUP BY player''')

def all_hs_classes(c):
  return query_rows(c,
                     '''SELECT player, COUNT(*) FROM class_highscores
                        GROUP BY player''')

def count_hs_combos(c, player):
  return query_first(c,
                     '''SELECT COUNT(*) FROM combo_highscores
                        WHERE player = %s''',
                     player)

def count_hs_combo_wins(c, player):
  return query_first(c,
                     '''SELECT COUNT(*) FROM game_combo_win_highscores
                        WHERE player = %s''',
                     player)

def count_hs_species(c, player):
  return query_first(c,
                     '''SELECT COUNT(*) FROM species_highscores
                        WHERE player=%s ''',
                     player)

def game_hs_species(c, player):
  return [ row_to_xdict(x) for x in
           query_rows(c,
                     ("SELECT " + ",".join(LOG_FIELDS)
                      + "  FROM species_highscores "
                      + " WHERE player=%s ORDER BY score DESC, charabbrev"),
                     player) ]

def count_hs_classes(c, player):
  return query_first(c,
                     '''SELECT COUNT(*) FROM class_highscores
                        WHERE player=%s''',
                     player)

def game_hs_classes(c, player):
  return [ row_to_xdict(x) for x in
           query_rows(c,
                     ("SELECT " + ",".join(LOG_FIELDS)
                      + "  FROM class_highscores "
                      + " WHERE player=%s ORDER BY score DESC, charabbrev"),
                     player) ]

###################################################################
# Super experimental team stuff. None of this is set in stone.

def drop_teams(c):
  query_do(c, 'TRUNCATE TABLE teams')

def team_exists(cursor, owner):
  """Returns the name of the team owned by 'owner', or None if there is no
  team owned by her."""
  row = query_row(cursor,
                  '''SELECT name FROM teams WHERE owner = %s''', owner)
  if row is None:
    return None
  return row[0]

def _add_player_to_team(cursor, team_owner, player):
  query_do(cursor,
           '''UPDATE players SET team_captain = %s
              WHERE name = %s''',
           team_owner, player)

def wrap_transaction(fn):
  """Given a function, returns a function that accepts a cursor and arbitrary
  arguments, calls the function with those args, wrapped in a transaction."""
  def transact(cursor, *args):
    result = None
    cursor.execute('BEGIN;')
    try:
      result = fn(cursor, *args)
      cursor.execute('COMMIT;')
    except:
      cursor.execute('ROLLBACK;')
      raise
    return result
  return transact

def create_team(cursor, team, owner_name):
  """Creates a team with the given name, owned by the named player."""
  loaddb.check_add_player(cursor, owner_name)
  def _create_team(cursor):
    query_do(cursor, '''INSERT INTO teams (owner, name) VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE name = %s''',
             owner_name, team, team)
    # Flush everyone from the team, in case a player was removed.
    query_do(cursor, '''UPDATE players SET team_captain = NULL
                         WHERE team_captain = %s''',
             owner_name)
    # Add the team owner herself to the team.
    _add_player_to_team(cursor, owner_name, owner_name)

  wrap_transaction(_create_team)(cursor)

def get_team_captains(c):
  return [r[0] for r in query_rows(c, 'SELECT owner FROM teams')]

def add_player_to_team(cursor, team_owner, player):
  """Adds the named player to the named team. Integrity checks are left to
  the db."""
  loaddb.check_add_player(cursor, player)
  wrap_transaction(_add_player_to_team)(cursor, team_owner, player)

def players_in_team(cursor, team_owner):
  """Returns a list of all the players in the team, with the team's
  owner first."""
  if not team_owner:
    raise Exception, "Team owner not provided!"
  prows = query_rows(cursor,
                     '''SELECT name FROM players
                        WHERE team_captain = %s''',
                     team_owner)
  players = [x[0] for x in prows if x[0].lower() != team_owner.lower()]
  players.insert(0, team_owner)
  return players

def get_clan_info(c, player):
  """Given a player name, returns a tuple of clan name and a list of
  players in the clan, with clan captain first, or None if the player is
  not in a clan."""
  captain = query_row(c, '''SELECT team_captain FROM players
                            WHERE name = %s''',
                      player)
  if captain is None or captain[0] is None:
    return None

  captain = captain[0]

  team_name = query_row(c, '''SELECT name FROM teams WHERE owner = %s''',
                        captain)
  if team_name is None or team_name[0] is None:
    return None

  team_name = team_name[0]
  return (team_name, players_in_team(c, captain))

def find_remaining_gods(used_gods):
  used_god_set = set([x or 'No God' for x in used_gods])
  return [god for god in crawl.GODS if god not in used_god_set]

def player_ziggurat_deepest(c, player):
  return query_first_def(c, 0,
                         '''SELECT deepest FROM ziggurats WHERE player = %s''',
                         player)

def get_top_ziggurats(c):
  rows = query_rows(c, '''SELECT player, place, deepest, zig_time
                            FROM best_ziggurat_dives
                           LIMIT 3''')
  # Convert to lists for doctoring.
  rows = [list(x) for x in rows]
  for r in rows:
    # Distinguish between entering and leaving ziggurat levels.
    if r[2] % 2 == 1:
      r[1] += " (out)"
  return [[x[0], x[1], x[3]] for x in rows]

def player_ziggurat_dive_pos(c, player):
  return find_place([x[0] for x in get_top_ziggurats(c)], player)

def player_rune_dive_best(c):
  return query_rows(c, '''SELECT player FROM youngest_rune_finds
                                      LIMIT 3''')

def player_rune_dive_pos(c, player):
  return find_place(player_rune_dive_best(c), player)

def youngest_rune_finds(c):
  return query_rows(c, '''SELECT player, rune, xl, rune_time
                            FROM youngest_rune_finds LIMIT 3''')

def player_deaths_to_uniques_best(c):
  """Returns the players who have died to the most uniques and the number of
  distinct uniques they've died to."""
  return query_rows(c, '''SELECT player, ndeaths, death_time
                            FROM most_deaths_to_uniques''')

def most_deaths_to_uniques(c):
  """Returns the players who have died to the most uniques and the distinct
  uniques they've died to, sorted in alphabetical order."""
  players = [[r[0], r[2]] for r in player_deaths_to_uniques_best(c)]
  rows = query_rows(c, '''SELECT player, uniq
                            FROM deaths_to_uniques
                           WHERE player IN
                                 (SELECT player FROM most_deaths_to_uniques)''')
  pmap = { }
  for player, uniq in rows:
    ulist = pmap.get(player) or set()
    ulist.add(uniq)
    pmap[player] = ulist
  result = [[x[0], pmap[x[0]], x[1]] for x in players]
  for r in result:
    r[1] = list(r[1])
    r[1].sort()
  return result

def player_deaths_to_uniques_pos(c, player):
  return find_place(
    player_deaths_to_uniques_best(c), player)

def register_maxed_skill(c, player, sk):
  if not query_first_def(c, None, '''SELECT player
                                       FROM player_maxed_skills
                                      WHERE player = %s AND skill = %s''',
                         player, sk):
    query_do(c, '''INSERT INTO player_maxed_skills (player, skill)
                                            VALUES (%s, %s)''',
             player, sk)

def register_fifteen_skill(c, player, sk):
  if not query_first_def(c, None, '''SELECT player
                                       FROM player_fifteen_skills
                                      WHERE player = %s AND skill = %s''',
                         player, sk):
    query_do(c, '''INSERT INTO player_fifteen_skills (player, skill)
                                            VALUES (%s, %s)''',
             player, sk)

def clan_maxed_skills(c, captain):
  skills = query_first_col(c, '''SELECT DISTINCT skill
                                   FROM player_maxed_skills ps, players p
                                  WHERE ps.player = p.name
                                    AND p.team_captain = %s''',
                           captain)
  return skills

def get_clan_banners(c, captain):
  return query_first_col(c, '''SELECT banner FROM clan_banners
                                WHERE team_captain = %s
                                ORDER BY prestige DESC, banner''',
                         captain)

def get_player_banners(c, player):
  return query_first_col(c, '''SELECT banner FROM player_banners
                                WHERE player = %s
                                ORDER BY prestige DESC, banner''',
                         player)

def player_banners_awarded(c):
  """Returns a list of tuples as [(banner_name, [list of players]), ...]
  ordered by descending order of banner prestige."""
  banner_rows = query_rows(c, '''SELECT banner, player
                                 FROM player_banners
                                 ORDER BY prestige DESC, banner, player''')
  banners = []
  for row in banner_rows:
    banner_name, player = row
    if not banners or banner_name != banners[-1][0]:
      banners.append( (banner_name, []) )
    banners[-1][1].append(player)
  return banners

def clan_player_banners(c):
  """Returns a list of tuples as [(banner_name, player_name)] for players
  in the top three clans."""
  banner_rows = query_rows(c, '''SELECT c.banner, p.name FROM
                                 clan_banners AS c, players AS p
                                 WHERE c.team_captain = p.team_captain''')
  return banner_rows

def get_saints(c, captain):
  rows = query_rows_with_ties(c, '''SELECT name, score_full FROM players
                                    WHERE team_captain = %s
                                    AND score_full >= 100''',
                              'score_full', 1, 1, captain)
  return [x[0] for x in rows]

def get_harvesters(c):
  rows = query_rows(c, '''SELECT p.name, p.team_captain FROM
                          players AS p, clan_unique_kills AS c
                          WHERE c.kills >= %s
                          AND c.team_captain = p.team_captain''',
                    len(uniq.UNIQUES))
  return [x[0] for x in rows]

def player_distinct_gods(c, player):
  """Returns the list of gods that the player has reached max piety with (no Xom)."""
  gods = query_first_col(c, '''SELECT DISTINCT noun
                                          FROM milestones
                                         WHERE player = %s
                                           AND verb = 'god.maxpiety' ''',
                         player)
  return gods

def player_distinct_renounced_gods(c, player):
  return query_first_col(c, '''SELECT DISTINCT noun
                                 FROM milestones
                                WHERE player = %s
                                  AND verb = 'god.renounce' ''',
                         player)

def player_distinct_mollified_gods(c, player):
  return query_first_col(c, '''SELECT DISTINCT noun
                                 FROM milestones
                                WHERE player = %s
                                  AND verb = 'god.mollify'
                                  AND (noun != god OR god IS NULL)''',
                         player)

def game_did_visit_lair(c, player, start_time):
  return query_first(c, '''SELECT COUNT(*)
                             FROM milestones
                            WHERE player = %s
                              AND start_time = %s
                              AND verb = 'br.enter' AND noun = 'Lair' ''',
                     player, start_time)

def game_did_visit_branch(c, player, start_time):
  return query_first(c, '''SELECT COUNT(*)
                             FROM milestones
                            WHERE player = %s
                              AND start_time = %s
                              AND verb = 'br.enter' 
                              AND ((noun = 'Temple') OR (noun = 'Lair')
                                  OR (noun = 'Orc')
                                  OR (noun = 'Vault')) ''',
                     player, start_time)

def count_deaths_to_distinct_uniques(c, player):
  return query_first(c, '''SELECT COUNT(DISTINCT uniq)
                             FROM deaths_to_uniques
                             WHERE player = %s''',
                     player)

def lookup_deaths_to_distinct_uniques(c, player):
  return query_first_def(c, 0,
                         '''SELECT ndeaths
                              FROM deaths_to_distinct_uniques
                             WHERE player = %s''',
                         player)

def update_deaths_to_distinct_uniques(c, player, ndeaths, time):
  query_do(c, '''INSERT INTO deaths_to_distinct_uniques
                      VALUES (%s, %s, %s)
                 ON DUPLICATE KEY UPDATE ndeaths = %s, death_time = %s ''',
           player, ndeaths, time, ndeaths, time)

def update_active_streak(c, player, end_time, streak_len):
    query_do(c, '''INSERT INTO active_streaks
                             (player, streak_time)
                      VALUES (%s, %s)
                 ON DUPLICATE KEY UPDATE streak = %s,
                                         streak_time = %s''',
           player, end_time, streak_len, end_time)

def kill_active_streak(c, player):
  query_do(c, '''DELETE FROM active_streaks WHERE player = %s''', player)

def find_most_recent_character_since(c, player):
  mile = query_row(c, '''SELECT start_time, src
                          FROM whereis_table
                         WHERE player = %s
                      ORDER BY mile_time DESC''', player)
  if not mile:
    return None
  last_game = query_row(c, '''SELECT start_time
                          FROM last_game_table
                         WHERE player = %s AND src = %s''', player, mile[1])
  if last_game and last_game[0] >= mile[0]:
    return None  
  return query_first(c, '''SELECT charabbrev
                             FROM milestones
                            WHERE player = %s
                              AND start_time = %s''', player, mile[0])
