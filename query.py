# Library to query the database and update scoring information. Raw data entry
# from logfile and milestones is done in loaddb.py, this is for queries and
# post-processing.

import logging
from logging import debug, info, warn, error

import loaddb
from loaddb import Query, query_do, query_first, query_row, query_rows

import crawl_utils

import MySQLdb

# Number of unique uniques
MAX_UNIQUES = 43
MAX_RUNES = 15

LOG_FIELDS = [ 'source_file' ] + [ x[1] for x in loaddb.LOG_DB_MAPPINGS ]

def _cursor():
  """Easy retrieve of cursor to make interactive testing easier."""
  d = loaddb.connect_db()
  return d.cursor()

def win_query(selected, order_by = None,
              player=None, character_race=None,
              character_class=None, runes=None,
              before=None, limit=None):
  query = Query("SELECT " + selected + " FROM games " +
                "WHERE killertype='winning' ")
  if player:
    query.append(' AND player=%s', player)
  if (character_race):
    query.append(' AND race=%s', character_race)
  if (character_class):
    query.append(' AND class=%s', character_class)
  if (runes):
    query.append(' AND runes >= %s', runes)
  if before:
    query.append(' AND end_time < %s', before)
  if order_by:
    query.append(' ' + order_by)
  if limit:
    query.append(" LIMIT %d" % limit)
  return query

def get_top_streaks(c, how_many = 10):
  streaks = query_rows(c, '''SELECT player, streak, streak_time
                             FROM streaks
                             ORDER BY streak DESC, streak_time
                             LIMIT %d''' % how_many)
  # Convert tuples to lists.
  streaks = [ list(x) for x in streaks ]
  # And the fourth item in each row has to be a list of the streak games.
  # And haha, you thought this was easy? :P
  for streak in streaks:
    streak.append( get_streak_games(c, streak[0], streak[2]) )
  return streaks

def get_top_clan_scores(c, how_many=3):
  clans = query_rows(c, '''SELECT name, owner, total_score
                           FROM teams
                           ORDER BY total_score DESC
                           LIMIT %d''' % how_many)
  return clans

def get_top_clan_unique_kills(c, how_many=3):
  return query_rows(c, '''SELECT c.name, u.team_captain, u.kills
                          FROM teams c, clan_unique_kills u
                          WHERE c.owner = u.team_captain
                          ORDER BY u.kills DESC
                          LIMIT %d''' % how_many)

def get_top_clan_combos(c, how_many = 3):
  return query_rows(c, '''SELECT c.name, hs.team_captain, hs.combos
                          FROM teams c, combo_hs_clan_scoreboard hs
                          WHERE c.owner = hs.team_captain
                          ORDER BY hs.combos DESC
                          LIMIT %d''' % how_many)

def _canonicalize_player_name(c, player):
  row = query_row(c, '''SELECT name FROM players WHERE name = %s''',
                  player)
  if row:
    return row[0]
  return None

canonicalize_player_name = \
    crawl_utils.Memoizer(_canonicalize_player_name, lambda args: args[1:])

def get_top_players(c, how_many=10):
  return query_rows(c,
                    '''SELECT name, score_full FROM players
                       ORDER BY score_full DESC
                       LIMIT %d''' % how_many)

def get_top_unique_killers(c, how_many=3):
  return query_rows(c,
                    '''SELECT player, nuniques, kill_time FROM kunique_times
                       ORDER BY nuniques DESC, kill_time
                       LIMIT %d''' % how_many)

def get_top_combo_highscorers(c, how_many=3):
  return query_rows(c,
                    '''SELECT player, nscores FROM combo_hs_scoreboard
                       ORDER BY nscores DESC LIMIT %d''' % how_many)

def get_deepest_xl1_games(c, how_many=3):
  return find_games(c, xl = 1, sort_max = 'lvl', limit = how_many)

def get_streak_games(c, player, end_time):
  q = Query('SELECT ' + ",".join(LOG_FIELDS) + ' FROM games ' +
            '''WHERE player = %s
               AND end_time >
                     (SELECT MAX(end_time) FROM games
                      WHERE player = %s
                      AND end_time < %s
                      AND killertype != 'winning')
               AND end_time <= %s
               ORDER BY end_time''',
            player, player, end_time, end_time)
  return [ row_to_xdict(x) for x in q.rows(c) ]

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

def row_to_xdict(row):
  return dict( zip(LOG_FIELDS, row) )

def find_games(c, sort_min=None, sort_max=None, limit=1, **dictionary):
  """Finds all games matching the supplied criteria, all criteria ANDed
  together."""

  if sort_min is None and sort_max is None:
    sort_min = 'end_time'

  query = Query('SELECT ' + ",".join(LOG_FIELDS) + ' FROM games')
  where = ''
  values = []
  for key, value in dictionary.items():
    if len(where):
      where += ' AND '
    where += key + " = %s"
    values.append(value)

  order_by = ''
  if sort_min:
    order_by += ' ORDER BY ' + sort_min
  elif sort_max:
    order_by += ' ORDER BY ' + sort_max + ' DESC'

  if where:
    query.append(' WHERE ' + where, *values)

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

def get_points(index, *points):
  if index >= 0 and index < len(points):
    return points[index];
  return 0

def assign_points(cursor, point_source, name, points):
  """Add points to a player's points in the db"""
  if points > 0:
    debug("%s: %d points [%s]" % (name, points, point_source))
    query_do(cursor,
             """UPDATE players
                SET score_base = score_base + %s
                WHERE name = %s""",
             points, name)

def assign_team_points(cursor, point_source, name, points):
  """Add points to a players team in the db.  The name refers to the player, not the team"""
  if points > 0:
    debug("TEAM %s: %d points [%s]" % (name, points, point_source))
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
                     player, unique) > 0

def player_count_runes(cursor, player, rune=None):
  """Counts the number of times the player has found runes (or a specific
  rune."""
  q = Query('''SELECT COUNT(rune) FROM rune_finds
               WHERE player = %s''', player)
  if rune:
    q.append(' AND rune = %s', rune)

  return q.first(cursor)

def find_place(rows, player):
  if rows is None:
    return -1
  p = [r[0] for r in rows]
  if player in p:
    return p.index(player)
  else:
    return -1

def player_fastest_realtime_win_pos(c, player):
  return find_place(query_rows(c, 'SELECT player FROM fastest_realtime'),
                    player)

def player_fastest_turn_win_pos(c, player):
  return find_place(query_rows(c, 'SELECT player FROM fastest_turncount'),
                    player)

def player_hs_combo_pos(c, player):
  return find_place(query_rows(c, 'SELECT player FROM combo_hs_scoreboard'),
                    player)

def player_streak_pos(c, player):
  return find_place(query_rows(c, 'SELECT player FROM streak_scoreboard'),
                    player)

def clan_combo_pos(c, owner):
  return find_place(query_rows(c,
                               '''SELECT team_captain FROM
                                  combo_hs_clan_scoreboard'''),
                    owner)

def clan_unique_pos(c, owner, limit=3):
  return find_place(query_rows(c,
                               '''SELECT team_captain FROM
                                  clan_unique_kills LIMIT %d''' % limit),
                    owner)

def count_hs_combos(c, player):
  return query_first(c,
                     '''SELECT COUNT(*) FROM game_combo_highscores
                        WHERE player = %s''',
                     player)

def count_hs_combo_wins(c, player):
  return query_first(c,
                     '''SELECT COUNT(*) FROM game_combo_win_highscores
                        WHERE player = %s''',
                     player)

def count_hs_species(c, player):
  return query_first(c,
                     '''SELECT COUNT(*) FROM game_species_highscores
                        WHERE player=%s''',
                     player)

def count_hs_classes(c, player):
  return query_first(c,
                     '''SELECT COUNT(*) FROM game_class_highscores
                        WHERE player=%s''',
                     player)

###################################################################
# Super experimental team stuff. None of this is set in stone.

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
    cursor.execute('BEGIN;')
    try:
      fn(cursor, *args)
      cursor.execute('COMMIT;')
    except:
      cursor.execute('ROLLBACK;')
      raise
  return transact

def create_team(cursor, team, owner_name):
  """Creates a team with the given name, owned by the named player."""
  loaddb.check_add_player(cursor, owner_name)
  def _create_team(cursor):
    query_do(cursor, '''INSERT INTO teams (owner, name) VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE name = %s''',
             owner_name, team, team)
    # Add the team owner herself to the team.
    _add_player_to_team(cursor, owner_name, owner_name)

  wrap_transaction(_create_team)(cursor)

def get_team_owners(cursor, team):
  """Returns the owners of all teams with the given name."""
  rows = query_rows(cursor,
                    '''SELECT owner FROM teams WHERE name=%s''',
                    team)
  return [r[0] for r in rows]

def add_player_to_team(cursor, team_owner, player):
  """Adds the named player to the named team. Integrity checks are left to
  the db."""
  loaddb.check_add_player(cursor, player)
  wrap_transaction(_add_player_to_team)(cursor, team_owner, player)

def players_in_team(cursor, team_owner):
  """Returns a list of all the players in the team, with the team's
  owner first."""
  prows = query_rows(cursor,
                     '''SELECT name FROM players
                        WHERE team_owner = %s''',
                     team_owner)
  players = [x[0] for x in prows]
  players.remove(team_owner)
  players.insert(0, team_owner)
  return players
