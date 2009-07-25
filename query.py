# Library to query the database and update scoring information. Raw data entry
# from logfile and milestones is done in loaddb.py, this is for queries and
# post-processing.

import logging
from logging import debug, info, warn, error

import loaddb
from loaddb import Query, query_do, query_first, query_row, query_rows

import crawl
import crawl_utils
import uniq
import os.path
import re

# Number of unique uniques
MAX_UNIQUES = 43
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

def canonical_where_name(name):
  test = '%s/%s' % (crawl_utils.RAWDATA_PATH, name)
  if os.path.exists(test):
    return name
  names = os.listdir(crawl_utils.RAWDATA_PATH)
  names = [ x for x in names if x.lower() == name.lower() ]
  if names:
    return names[0]
  else:
    return None

def whereis_player(name):
  name = canonical_where_name(name)
  if name is None:
    return name

  where_path = '%s/%s/%s.where' % (crawl_utils.RAWDATA_PATH, name, name)
  if not os.path.exists(where_path):
    return None

  try:
    f = open(where_path)
    try:
      line = f.readline()
      d = loaddb.apply_dbtypes( loaddb.xlog_dict(line) )
      if d.get('time'):
        d['time'] = loaddb.datetime.to_sql(d['time'])
      return _filter_invalid_where(d)
    finally:
      f.close()
  except:
    return None

def did_change_god(c, game):
  """Returns true if the player changed gods during the game, by checking
  for a god.renounce milestone."""
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start = %s
                            AND verb = 'god.renounce' ''',
                      game['player'], game['start_time']) > 0)

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

def get_player_won_gods(c, player):
  "Returns the names of all the gods that the player has won games with,
wins counting only if the player has not switched gods during the game."
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

def get_fastest_time_player_games(c):
  fields = ",".join([ 'g.' + x for x in LOG_FIELDS ])
  games = query_rows(c, '''SELECT %s FROM fastest_realtime f, games g
                           INNER JOIN ON f.id = g.id''' % fields)
  return [ row_to_xdict(r) for r in games ]

def get_fastest_turn_player_games(c):
  fields = ",".join([ 'g.' + x for x in LOG_FIELDS ])
  games = query_rows(c, '''SELECT %s FROM fastest_turncount f, games g
                           INNER JOIN ON f.id = g.id''' % fields)
  return [ row_to_xdict(r) for r in games ]

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

def get_top_clan_scores(c, how_many=10):
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

def get_combo_scores(c, how_many = None):
  query = Query("SELECT " + ",".join(LOG_FIELDS) +
                """ FROM game_combo_highscores
                   ORDER BY score DESC""")
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

  def combine_deaths(killer, p, n):
    if p[1] == 'beam':
      ranged = p[2]
      melee = n[2]
    else:
      ranged = n[2]
      melee = p[2]
    return "%s (%d melee, %d ranged)" % (killer, melee, ranged)

  # Now to fix up the rows.
  clean_rows = [ ]
  last = None

  total = 0
  for r in rows:
    killer = r[0]
    total += r[2]
    if last and last[0] == killer:
      clean_rows.pop()
      killer = combine_deaths(killer, last, r)
      clean_rows.append( [ killer, last[2] + r[2], r[3] ] )
    else:
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
                     COALESCE((SELECT MAX(end_time) FROM games
                               WHERE player = %s
                               AND end_time < %s
                               AND killertype != 'winning'), DATE('19700101'))
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

def get_winning_games(c, **selectors):
  """Returns the games for wins matching the provided criteria, ordered
  with earlier wins first. Exactly the same as get_wins, but returns
  the xlog dictionaries instead of the charabbrev"""
  return find_games(c, sort_max='end_time', limit=None,
                    killertype='winning', **selectors)

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

  query = Query('SELECT ' + ",".join(LOG_FIELDS) + ' FROM games')
  where = ''
  values = []

  def append_where(where, clause, *newvalues):
    if len(where):
      where += ' AND '
    where += clause
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

def calc_perc(num, den):
  if den <= 0:
    return 0.0
  else:
    return num * 100.0 / den

def get_all_game_stats(c):
  played = query_first(c, '''SELECT COUNT(*) FROM games''')
  won = query_first(c, """SELECT COUNT(*) FROM games
                          WHERE killertype='winning'""")
  win_perc = "%.2f%%" % calc_perc(won, played)
  return { 'played' : played,
           'won' : won,
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
                    '''SELECT name, (score_full + team_score_base) points
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

def audit_flush_player(c, player):
  """Discards temporary points assigned to the player from the audit table."""
  query_do(c, '''DELETE FROM player_points
                 WHERE player = %s AND temp = 1''',
           player)

def audit_flush_clan(c, captain):
  query_do(c, '''DELETE FROM clan_points WHERE captain = %s''', captain)

def log_temp_points(c, who, what, points):
  if points > 0:
    say_points(who, what, points)
    audit_record_points(c, who, what, points, True)
  return points

def log_temp_team_points(c, who, what, points):
  if points > 0:
    say_points(who + '(c)', what, points)
    audit_record_points(c, who, what, points, True, credited = 'team_points')
  return points

def log_temp_clan_points(c, captain, what, points):
  if points > 0:
    say_points('CLAN:' + captain, what, points)
    clan_audit_record_points(c, captain, what, points)
  return points

def get_points(index, *points):
  if index >= 0 and index < len(points):
    return points[index];
  return 0

def assign_points(cursor, point_source, name, points):
  """Add points to a player's points in the db"""
  if points > 0:
    debug("%s: %d points [%s]" % (name, points, point_source))
    audit_record_points(cursor, name, point_source, points, False)
    query_do(cursor,
             """UPDATE players
                SET score_base = score_base + %s
                WHERE name = %s""",
             points, name)

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

def player_uniques_killed(c, player):
  rows = query_rows(c, '''SELECT DISTINCT monster FROM kills_of_uniques
                          WHERE player = %s ORDER BY monster''',
                    player)
  return [ row[0] for row in rows ]

def uniques_unkilled(uniques_killed):
  killset = set(uniques_killed)
  return [ u for u in uniq.UNIQUES if u not in killset ]

def player_xl1_dive_pos(c, player):
  return find_place([ [ g['player'] ] for g in get_deepest_xl1_games(c) ],
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
