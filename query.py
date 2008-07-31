# Library to query the database and update scoring information. Raw data entry
# from logfile and milestones is done in loaddb.py, this is for queries and
# post-processing.

import logging
from logging import debug, info, warn, error

import loaddb
from loaddb import Query, query_do, query_first, query_row

import MySQLdb

# Number of unique uniques
MAX_UNIQUES = 43
MAX_RUNES = 15

LOG_FIELDS = [ x[1] for x in loaddb.LOG_DB_MAPPINGS ]

def _cursor():
  """Easy retrieve of cursor to make interactive testing easier."""
  d = loaddb.connect_db()
  return d.cursor()

def win_query(selected, order_by = None,
              player=None, character_race=None,
              character_class=None, runes=None,
              before=None):
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
  return query

def wins_in_streak_before(c, player, before):
  """Returns all the wins in the streak before the given game. Caller
  must ensure that there actually are wins before this game!"""
  query = Query('''SELECT charabbrev FROM games
                   WHERE player = %s
                   AND end_time >
                         (SELECT MAX(end_time) FROM games
                          WHERE player = %s
                          AND end_time < %s
                          AND killertype != 'winning')
                   AND end_time < %s
                   ORDER BY end_time''',
                player, player, before, before)
  return [ x[0] for x in query.rows(c) ]

def count_wins(c, **selectors):
  """Return the number wins recorded for the given player, optionally with
     a specific race, class, minimum number of runes, or any combination"""
  return win_query('COUNT(start_time)', **selectors).count(c)

def get_wins(c, **selectors):
  return [ x[0] for x in
           win_query('charabbrev', order_by = 'ORDER BY end_time',
                     **selectors).rows(c) ]

def row_to_xdict(row):
  return dict( zip(LOG_FIELDS, row) )

def find_games(c, sort_min=None, sort_max=None, limit=1, **dictionary):
  """Finds all games matching the supplied criteria, all criteria ANDed
  together."""
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
    order_by += ' ORDER BY ' + sort
  elif sort_max:
    order_by += ' ORDER BY ' + sort_max + ' DESC'

  if where:
    query.append(' WHERE ' + where, *values)

  if order_by:
    query.append(order_by)

  if limit:
    query.append(' LIMIT %d' % limit)

  print "Running " + query.query
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

def assign_points(cursor, point_source, name, points):
  """Add points to a player's points in the db"""
  if points > 0:
    info("%s: %d points [%s]" % (name, points, point_source))
    query_do(cursor,
             """UPDATE players
                SET score_base = score_base + %s
                WHERE name = %s""",
             points, name)

def assign_team_points(cursor, point_source, name, points):
  """Add points to a players team in the db.  The name refers to the player, not the team"""
  if points > 0:
    info("TEAM %s: %d points [%s]" % (name, points, point_source))
    query_do(cursor,
             """UPDATE players
                SET team_score_base = team_score_base + %s
                WHERE name=%s;""",
             points, name)

def has_killed_unique(cursor, player, unique):
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
