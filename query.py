# Library to query the database and update scoring information. Raw data entry
# from logfile and milestones is done in loaddb.py, this is for queries and
# post-processing.

import logging
from logging import debug, info, warn, error

import loaddb
from loaddb import Query, query_do, query_first, query_row

import MySQLdb

def count_wins(c, player, character_race=None,
               character_class=None, runes=None):
  """Return the number wins recorded for the given player, optionally with
     a specific race, class, minimum number of runes, or any combination"""
  query = Query('''SELECT COUNT(start_time) FROM games
                   WHERE killertype='winning' AND player=%s''',
                player)
  if (character_race):
    query.append(' AND race=%s', character_race)
  if (character_class):
    query.append(' AND class=%s', character_class)
  if (runes):
    query.append(' AND runes >= %s', runes)
  query.append(';')
  return query.count(c)

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

def player_exists(c, name):
  """Return true if the player exists in the player table"""
  query = Query("""SELECT name FROM players WHERE name=%s;""",
                name)
  return query.row(c) is not None

def add_player(c, name):
  """Add the given player with no score yet"""
  query_do(c,
           """INSERT INTO players (name, score_base, team_score_base)
              VALUES (%s, 0, 0);""",
           name)

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

def assign_points(cursor, name, points):
  """Add points to a player's points in the db"""
  query_do(cursor,
           """UPDATE players
              SET score_base = score_base + %s
              WHERE name = %s""",
           points, name)

def assign_team_points(cursor, name, points):
  """Add points to a players team in the db.  The name refers to the player, not the team"""
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

def team_exists(cursor, team_name):
  row = query_row(cursor,
                  '''SELECT id FROM teams WHERE name = %s''', team_name)
  return row is not None

def _add_player_to_team(cursor, team, player):
  query_do(cursor,
           '''UPDATE players
              SET team = (SELECT id FROM teams WHERE name = %s)
              WHERE name = %s''',
           team, player)

def wrap_transaction(fn):
  """Given a function, returns a function that accepts a cursor and arbitrary
  arguments, calls the function with those args, wrapped in a transaction."""
  def transact(cursor, *args):
    cursor.execute('BEGIN';)
    try:
      fn(cursor, *args)
      cursor.execute('COMMIT;')
    except:
      cursor.execute('ROLLBACK;')
      raise
  return transact

def create_team(cursor, team, owner_name):
  """Creates a team with the given name, owned by the named player."""
  check_add_player(cursor, owner_name)
  def _create_team(cursor):
    query_do(cursor, 'INSERT INTO teams (name) VALUES (%s)', team)
    query_do(cursor, '''INSERT INTO team_owners (team, owner)
                        VALUES ((SELECT id FROM teams WHERE name = %s),
                                 %s)''',
             team, owner_name)
    # Add the team owner herself to the team.
    _add_player_to_team(cursor, team, owner_name)

  wrap_transaction(_create_team)(cursor)

def get_team_owner(cursor, team):
  row = query_row(cursor,
                  '''SELECT owner FROM team_owners
                     WHERE team = (SELECT id FROM teams
                                   WHERE name = %s)''',
                  team)
  if row is None:
    return None
  return row[0]

def check_add_player(cursor, player):
  """Checks whether a player exists in the players table,
  adds an entry if not, suppressing exceptions."""
  try:
    if not player_exists(cursor, player):
      add_player(cursor, player)
  except MySQLdb.IntegrityError:
    # We don't care, this just means someone else added the player
    # just now
    pass

def add_player_to_team(cursor, team, player):
  """Adds the named player to the named team. Integrity checks are left to
  the db."""
  check_add_player(cursor, player)
  wrap_transaction(_add_player_to_team)(cursor, team, player)

def players_in_team(cursor, team):
  """Returns a list of all the players in the team, with the team's
  owner first."""
  prows = query_rows(cursor,
                     '''SELECT name FROM players
                        WHERE team = (SELECT id FROM teams WHERE name = %s)''',
                     team)
  players = [x[0] for x in prows]
  leader = get_team_owner(cursor, team)
  players.remove(leader)
  players.insert(0, leader)
  return players
