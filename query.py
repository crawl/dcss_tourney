# coding=utf8

# Library to query the database and update scoring information. Raw data entry
# from logfile and milestones is done in loaddb.py, this is for queries and
# post-processing.

import logging
from logging import debug, info, warn, error

import loaddb
from loaddb import query_do, query_first, query_row, query_rows
from loaddb import query_rows_with_ties
from loaddb import query_first_col, query_first_def

from query_class import Query

import scoring_data
from scoring_data import INDIVIDUAL_CATEGORIES, MAX_CATEGORY_SCORE, CLAN_CATEGORIES

import combos
import crawl
import crawl_utils
import uniq
import os.path
import re
from datetime import datetime
import time
import json

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
  if (game_god == 'Xom' or game_god == 'Gozag' or game_god == 'No God') \
	and not did_renounce_god(c, game['name'], game['start'], game['end']):
    return game_god
  return get_first_max_piety(c, game['name'], game['start'])

def count_god_wins(c, god, start_time=None):
  q = Query('''SELECT COUNT(*) FROM player_won_gods
               WHERE god=%s''', god)
  if start_time:
    q.append(' AND win_time < %s', start_time)
  return q.first(c)

def is_unbeliever(c, game):
  if game.get('god'):
    return False
  if game['raceabbr'] == 'Dg':
    return False
  if did_change_god(c, game):
    return False
  return True

def did_change_god(c, game):
  """Returns true if the player changed gods during the game, by checking
  for a god.renounce or god.worship milestone."""
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND (verb = 'god.renounce'
                            OR verb = 'god.worship') ''',
                      game['name'], game['start']) > 0)

def did_renounce_god(c, name, start, end):
  """Returns true if the player renounced a god before end, by checking
  for a god.renounce milestone."""
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND verb = 'god.renounce'
			    AND milestone_time < %s ''',
                      name, start, end) > 0)

def did_worship_god(c, god, name, start, end):
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND (verb = 'god.renounce'
                            OR verb = 'god.worship')
                            AND noun = %s
                            AND milestone_time < %s ''',
                      name, start, god, end) > 0)

def did_use_ecumenical_altar(c, name, start, end):
  """Returns true if the player joined a new religion at an ecumenical
  altar."""
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND verb = 'god.ecumenical'
                            AND milestone_time < %s ''',
                      name, start, end) > 0)

def did_get_rune(c, rune, name, start, end):
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND verb = 'rune'
                            AND noun = %s
                            AND milestone_time < %s ''',
                      name, start, rune, end) > 0)

def did_exit_branch(c, br, name, start, end):
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND verb = 'br.exit'
                            AND noun = %s
                            AND milestone_time < %s ''',
                      name, start, br, end) > 0)

def did_enter_branch(c, br, name, start, end):
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND verb = 'br.enter'
                            AND noun = %s
                            AND milestone_time < %s ''',
                      name, start, br, end) > 0)

def branch_end_turn(c, br, name, start):
    return query_first(c, '''SELECT turn FROM milestones
                              WHERE player = %s AND start_time = %s
                                AND verb = 'br.end'
                                AND noun = %s ''', name, start, br)

def did_sacrifice(c, noun, name, start, end):
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND verb = 'sacrifice'
                            AND noun = %s
                            AND milestone_time < %s ''',
                      name, start, noun, end) > 0)

def did_champion(c, god, name, start, end):
  return (query_first(c,
                      '''SELECT COUNT(*) FROM milestones
                          WHERE player = %s AND start_time = %s
                            AND verb = 'god.maxpiety'
                            AND noun = %s
                            AND milestone_time < %s ''',
                      name, start, god, end) > 0)

def win_query(selected, order_by = None,
              player=None, charabbr=None, character_race=None, raceabbr=None,
              character_class=None, classabbr=None, runes=None,
              before=None, after=None, limit=None):

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
  if after:
    query.append(' AND start_time > %s', after)
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
                         "SELECT DISTINCT god FROM player_won_gods WHERE player = %s",
                         player)

def get_player_best_streak_games(c, player):
  streaks = list_all_streaks(c, player)
  if len(streaks) > 0:
    return streaks[0][3]
  return None

def player_top_scores(c, limit=5):
  return query_rows(c, '''SELECT player, score
                            FROM games
                        ORDER BY score DESC
                           LIMIT %d''' % limit)

def logfile_fields(prefix = None):
  if prefix:
    return ",".join([ prefix + x for x in LOG_FIELDS ])
  else:
    return ",".join(LOG_FIELDS)

def get_top_active_streaks(c, limit = None):
  streaks = list_all_streaks(c, None, True)
  if limit and len(streaks) > limit:
    streaks = streaks[:hlimit]
  return streaks

def get_top_streaks(c, limit = None):
  streaks = list_all_streaks(c)
  filtered_streaks = []
  for streak in streaks:
    if streak[0] in [s[0] for s in filtered_streaks]:
      continue
    filtered_streaks.append(streak)
  if limit and len(filtered_streaks) > limit:
    filtered_streaks = filtered_streaks[:limit]
  return filtered_streaks

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

def highscore(c, combo):
  return query_first_def(c, 0, '''SELECT score FROM games
                                  WHERE charabbrev = %s
                                  ORDER BY score DESC''',
                         combo)

def previous_combo_highscore(c, game):
  return query_row(c, '''SELECT player, score, killertype
                         FROM games
                         WHERE charabbrev = %s
                         AND end_time < %s
                         ORDER BY score DESC''',
                   game['char'], game['end'])

def previous_species_highscore(c, game):
  return query_row(c, '''SELECT player, score, killertype
                         FROM games
                         WHERE raceabbr = %s
                         AND end_time < %s
                         ORDER BY score DESC''',
                   game['char'][:2], game['end'])

def previous_class_highscore(c, game):
  return query_row(c, '''SELECT player, score, killertype
                         FROM games
                         WHERE MID(charabbrev,3,2) = %s
                         AND end_time < %s
                         ORDER BY score DESC''',
                   game['char'][2:], game['end'])

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

def get_top_players(c, how_many=10):
   return query_rows_with_ties(c,
                         '''SELECT name, score_full FROM players
                             WHERE score_full > 0''',
                             'score_full', how_many, 1)

def check_xl9_streak(c, player, start):
  mile = query_row(c, '''SELECT start_time
                           FROM milestones
                          WHERE player = %s
                            AND verb = 'begin'
                            AND milestone_time < %s
                       ORDER BY milestone_time DESC''', player, start)
  if not mile:
    return False
  game = query_row(c, '''SELECT end_time
                           FROM games
                          WHERE player = %s
                            AND xl > 8
                            AND end_time < %s
                            AND end_time > %s''', player, start, mile[0])
  if game:
    return True
  return False

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

def player_race_wins(c, name):
  return query_rows(c, """SELECT DISTINCT MID(charabbrev,1,2) FROM
       games WHERE killertype='winning' AND player=%s""", name)

def player_class_wins(c, name):
  return query_rows(c, """SELECT DISTINCT MID(charabbrev,3,2) FROM
       games WHERE killertype='winning' AND player=%s""", name)

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
    elif isinstance(value, (list, tuple)):
      if len(value) == 2 and value[0] == 'not':
        # TODO: make this less ad hoc somehow
        append_where(where, key + " != %s", value[1])
      else:
        append_where(where, key + " IN (" +
              ",".join(['%s'] * len(value)) + ")", *value)
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
  played = query_first(c, '''SELECT COUNT(*) FROM games WHERE killertype NOT IN ('quitting', 'leaving', 'wizmode')''')
  distinct_players = query_first(c, '''SELECT COUNT(DISTINCT player) FROM games WHERE killertype NOT IN ('quitting', 'leaving', 'wizmode')''')
  won = query_first(c, """SELECT COUNT(*) FROM games
                          WHERE killertype='winning'""")
  distinct_winners = query_first(c, """SELECT COUNT(DISTINCT player) FROM games
                                       WHERE killertype='winning'""")
  allrune_won = query_first(c, """SELECT COUNT(*) FROM games
                          WHERE killertype='winning' AND nrune=15""")
  allrune_distinct_winners = query_first(c, """SELECT COUNT(DISTINCT player) FROM games
                                       WHERE killertype='winning' and nrune=15""")

  win_perc = "%.2f%%" % calc_perc(won, played)
  allrune_win_perc = "%.2f%%" % calc_perc(allrune_won, played)
  played_text = "%d (%d players)" % (played, distinct_players)
  won_text = "%d (%d players)" % (won, distinct_winners)
  allrune_won_text = "%d (%d players)" % (allrune_won, allrune_distinct_winners)
  return { 'played' : played_text,
           'won' : won_text,
           'allrune_won': allrune_won_text,
           'win_perc' : win_perc,
           'allrune_win_perc': allrune_win_perc }

def get_all_player_stats(c):
  q = Query('''SELECT p.name, p.team_captain, t.name, p.score_full,
                      (SELECT COUNT(*) FROM games
                       WHERE player = p.name
                       AND killertype = 'winning') wincount,
                      (SELECT COUNT(*) FROM games
                       WHERE player = p.name) playcount
               FROM players p LEFT JOIN teams t
               ON p.team_captain = t.owner
               ORDER BY p.score_full DESC, p.name''')
  rows = [ list(r) for r in q.rows(c) ]
  clean_rows = [ ]
  for r in rows:
    captain = r[1]
    r = r[0:1] + r[2:]
    if captain is None:
      r[1] = ''
    else:
      r[1] = crawl_utils.linked_text(captain, crawl_utils.clan_link, r[1])
    r.append( "%.2f%%" % calc_perc( r[3], r[4] + 1 ) )
    clean_rows.append(r)
  return clean_rows

def get_clan_stats(c, captain):
  stats = { }
  points = query_row(c, '''SELECT total_score FROM teams
                           WHERE owner = %s''',
                     captain)
  if points is not None:
    stats['points'] = points[0]
    stats['rank1'] = query_first(c, '''SELECT COUNT(DISTINCT total_score) FROM teams
                                      WHERE total_score > %s''',
                                stats['points']) + 1
    stats['rank2'] = query_first(c, '''SELECT COUNT(DISTINCT total_score) FROM teams''')


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
  points = query_row(c, '''SELECT score_full
                           FROM players WHERE name = %s''',
                     name)
  if points is None:
    return { }

  stats = { }
  stats['points'] = points[0]
  stats['rank1'] = query_first(c, '''SELECT COUNT(DISTINCT score_full) FROM players
                                    WHERE score_full > %s''',
                              stats['points']) + 1
  stats['rank2'] = query_first(c, '''SELECT COUNT(DISTINCT score_full) FROM players''')

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

  stats['win_perc'] = "%.2f%%" % calc_perc(stats['won'], stats['played'] + 1)
  return stats

def get_player_ranks(c, name):
    """Returns a dictionary of player ranks in different categories"""
    ranks = query_row(c, '''SELECT '''
                          + ",".join([ ic.rank_column for ic in
                              INDIVIDUAL_CATEGORIES ])
                          + ''' FROM players WHERE name = %s''', name)
    if ranks is None:
        return None
    return dict(zip( [ ic.name for ic in INDIVIDUAL_CATEGORIES ], ranks))

def get_players(c):
  return [r[0] for r in
          query_rows(c, 'SELECT name FROM players')]

def get_clans(c):
  return [r[0] for r in query_rows(c, 'SELECT owner FROM teams')]

def is_god_repeated(c, player, god):
  """Returns true if the player has been credited as the champion of the
  specified god."""
  return query_first_def(c, False,
                         '''SELECT COUNT(*) FROM player_max_piety
                             WHERE player = %s AND COALESCE(god, '') = %s''',
                         player, god)

def is_god_win_repeated(c, player, god):
  """Returns true if the player has been credited as the winner of the
  specified god."""
  return query_first_def(c, False,
                         '''SELECT COUNT(*) FROM player_won_gods
                             WHERE player = %s AND COALESCE(god, '') = %s''',
                         player, god)

def record_won_god(c, player, god):
  if is_god_win_repeated(c, player, god):
    return False
  query_do(c, "INSERT INTO player_won_gods VALUES (%s, %s)", player, god)
  return True

def record_max_piety(c, player, start_time, god):
  if is_god_repeated(c, player, god):
    return False
  if get_first_max_piety(c, player, start_time) == god:
    query_do(c, "INSERT INTO player_max_piety VALUES (%s, %s)", player, god)
    return True
  return False

def get_first_max_piety(c, player, start_time):
  row = query_row(c,
                         '''SELECT noun, milestone_time FROM milestones
                            WHERE player = %s AND start_time = %s
                              AND verb = 'god.maxpiety'
                            ORDER BY milestone_time ASC''',
                         player, start_time)
  if row is None:
    return 'faithless'
  if (query_first(c,
                  '''SELECT COUNT(*) FROM milestones
                     WHERE player = %s AND start_time = %s
                       AND verb = 'god.renounce'
                       AND noun <> %s
                       AND milestone_time < %s''',
                  player, start_time, row[0], row[1]) > 0):
    return 'faithless'
  return row[0]

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

def player_count_invo_titles(c, player):
  return query_first(c, '''SELECT COUNT(DISTINCT title)
                             FROM games
                            WHERE player = %s
                              AND killertype = 'winning'
                              AND skill = 'Invocations' ''',
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

def player_uniques_killed(c, player):
  rows = query_rows(c, '''SELECT DISTINCT monster FROM kills_of_uniques
                          WHERE player = %s ORDER BY monster''',
                    player)
  return [ row[0] for row in rows ]

def clan_uniques_killed(c, captain):
  rows = query_rows(c, '''SELECT DISTINCT k.monster
                          FROM players p INNER JOIN kills_of_uniques k
                              ON p.name = k.player
                          WHERE p.team_captain = %s ORDER BY k.monster''',
                    captain)
  return [ row[0] for row in rows ]

def uniques_unkilled(uniques_killed):
  killset = set(uniques_killed)
  return [ u for u in uniq.UNIQUES if u not in killset ]

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
  info("Drop teams")
  query_do(c, 'DELETE FROM teams')

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
    raise Exception("Team owner not provided!")
  prows = query_rows(cursor,
                     '''SELECT name FROM players
                        WHERE team_captain = %s''',
                     team_owner)
  players = [x[0] for x in prows if x[0].lower() != team_owner.lower()]
  players.insert(0, team_owner)
  return players

def get_clan_info(c, player):
  """Given a player name, returns a tuple of:
  1. clan name
  2. list of players in the clan (with clan captain first)
  3. clan page URL
  or None if the player is not in a clan.
  """
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
  return (
    team_name,
    players_in_team(c, captain),
    crawl_utils.clan_link(team_name, captain),
  )

def find_remaining_gods(used_gods):
  used_god_set = set([x or 'No God' for x in used_gods])
  remaining = [god for god in crawl.GODS if god not in used_god_set]
  remaining.sort()
  return remaining

def player_ziggurat_deepest(c, player):
  return query_first_def(c, 0,
                         '''SELECT completed, deepest FROM ziggurats WHERE player = %s''',
                         player)

def clan_zig_depth(c, owner):
  return max([player_ziggurat_deepest(c, player) for player in players_in_team(c, owner)])

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
  return query_rows(c, '''SELECT banner, prestige FROM clan_banners
                                WHERE team_captain = %s
                                ORDER BY prestige DESC, banner''',
                         captain)

def get_player_banners(c, player):
  banners = query_rows(c, '''SELECT banner, prestige FROM player_banners
                             WHERE player = %s
                             ORDER BY prestige DESC, banner''',
                       player)
  if len(banners) > 0:
    for i in range(len(banners)):
      if banners[i][1] <= 3:
        i = i-1
        break
    if i < len(banners) - 1:
      banners = list(banners)
      banners.insert(i+1, ['header', 1])
      banners.append(['footer', 1])
  return banners

def player_banners_awarded(c):
  """Returns a list of tuples as [(banner_name, prestige, [list of players]), ...]
  ordered by descending order of banner prestige."""
  banner_rows = query_rows(c, '''SELECT banner, prestige, player
                                 FROM player_banners
                                 ORDER BY banner, prestige, player''')
  banners = []
  nemelex_banners = [('nemelex', i, []) for i in range(1,4)]
  inserted_nemelex = False
  for row in banner_rows:
    banner_name, prestige, player = row
    if banner_name >= 'nemeley' and not inserted_nemelex:
      for ban in nemelex_banners:
        if len(ban[2]) > 0:
          ban[2].sort(key = lambda e: e[0].upper())
          banners.append(ban)
      inserted_nemelex = True
    if len(banner_name) == 12 and banner_name[:7] == 'nemelex':
      combo = banner_name[-4:]
      found_player = False
      for p in nemelex_banners[prestige-1][2]:
        if player == p[0]:
          p[1].append(combo)
          found_player = True
          break
      if not found_player:
        nemelex_banners[prestige-1][2].append((player,[combo]))
    else:
      if not banners or banner_name != banners[-1][0] or prestige != banners[-1][1]:
        banners.append( (banner_name, prestige, []) )
      banners[-1][2].append((player,[]))
  return banners

def clan_player_banners(c):
  """Returns a list of tuples as [(banner_name, player_name)] for players
  in the top three clans."""
  banner_rows = query_rows(c, '''SELECT c.banner, c.prestige, p.name FROM
                                 clan_banners AS c, players AS p
                                 WHERE c.team_captain = p.team_captain''')
  return banner_rows

def get_saints(c, captain):
  rows = query_rows_with_ties(c, '''SELECT name, score_full FROM players
                                    WHERE team_captain = %s
                                    AND score_full > 0''',
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

def game_did_visit_lair(c, player, start_time, before_time=None):
  if before_time:
    return query_first(c, '''SELECT COUNT(*)
                               FROM milestones
                              WHERE player = %s
                                AND start_time = %s
                                AND milestone_time < %s
                                AND verb = 'br.enter' AND noun = 'Lair' ''',
                     player, start_time, before_time)
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
                              AND ((noun = 'Lair')
                                  OR (noun = 'Orc')
                                  OR (noun = 'Vaults')) ''',
                     player, start_time)

def count_gods_abandoned_no_rejoin(c, player):
  return query_first(c,
      '''SELECT COUNT(DISTINCT m.noun)
           FROM milestones AS m
LEFT OUTER JOIN milestones AS m2
             ON m.player = m2.player AND m.game_id = m2.game_id
                AND m.turn < m2.turn
          WHERE m.player = %s
            AND m.verb = 'god.renounce'
            AND NOT (m2.verb = 'god.worship' AND m2.noun = m.noun)
            AND m.noun NOT IN ('the Shining One', 'Zin', 'Elyvilon',
                             'Ru', 'Beogh')''', player)

def count_gods_mollified(c, player):
  return query_first(c, '''SELECT COUNT(DISTINCT t.noun) FROM
                             (SELECT noun,
                                     ROW_NUMBER() OVER (PARTITION BY src,
                                     start_time ORDER BY milestone_time) AS ord
                                     FROM milestones
                                    WHERE player = %s
                                      AND verb = 'god.mollify'
                                      AND (noun != god OR god IS NULL)
                                      AND noun NOT IN ('the Shining One',
                                      'Zin', 'Elyvilon', 'Ru', 'Beogh')) AS t
                             WHERE t.ord=1''',
                             player)

def next_start_time(c, player, end_time):
  mile = query_row(c, '''SELECT start_time
                           FROM milestones
                          WHERE player = %s
                            AND verb = 'begin'
                            AND milestone_time > %s
                       ORDER BY milestone_time''', player, end_time)
  if not mile:
    return None
  return mile[0]

def next_start_char(c, player, end_time):
  mile = query_row(c, '''SELECT charabbrev
                           FROM milestones
                          WHERE player = %s
                            AND verb = 'begin'
                            AND milestone_time > %s
                       ORDER BY milestone_time''', player, end_time)
  if not mile:
    return None
  return mile[0]

def next_game_in_streak(c, game):
  start_time = next_start_time(c, game['player'], game['end_time'])
  if not start_time:
    return None
  row = query_row(c, "SELECT " + ",".join(LOG_FIELDS)
                      + """  FROM games
                         WHERE player = %s
                         AND start_time = %s""", game['player'], start_time)
  if not row:
    return None
  return row_to_xdict(row)

# Streak length is currently defined to be
# min(# of distinct races, # of distinct classes).
def compute_streak_length(games):
  races = set([game['charabbrev'][0:2] for game in games])
  classes = set([game['charabbrev'][2:] for game in games])
  return min(len(races), len(classes))

def list_all_streaks(c, name=None, active=False):
  if name:
    wins = get_winning_games(c, player = name)
  else:
    wins = get_winning_games(c)
  streak_list = []
  for game in wins:
    next_char = None
    breaker = None
    if not win_is_streak(c, game['player'], game['start_time']):
      new_streak = [game]
      while True:
        next_game = next_game_in_streak(c,new_streak[-1])
        if next_game:
          if next_game['killertype'] == 'winning':
            new_streak.append(next_game)
            is_active = True
          else:
            is_active = False
            breaker = next_game
            break
        else:
          is_active = True
          break
      if is_active:
        next_char = next_start_char(c,game['player'],new_streak[-1]['end_time'])
      length = compute_streak_length(new_streak)
      if length < 2:
        continue
      if not active or is_active:
        streak_list.append({ 'player': game['player'], 'length': length,
                           'end_time': new_streak[-1]['end_time'],
                           'games': new_streak, 'next_char': next_char,
                           'is_active': is_active, 'breaker': breaker})

  streak_list.sort(key=lambda row: (-row['length'],row['end_time']))
  return streak_list

def win_is_streak(c, player, start):
  mile = query_row(c, '''SELECT start_time
                           FROM milestones
                          WHERE player = %s
                            AND verb = 'begin'
                            AND milestone_time < %s
                       ORDER BY milestone_time DESC''', player, start)
  if not mile:
    return False
  game = query_row(c, '''SELECT end_time
                           FROM games
                          WHERE player = %s
                            AND killertype = 'winning'
                            AND end_time < %s
                            AND end_time > %s''', player, start, mile[0])
  if game:
    return True
  return False

def check_ash_banners(c, name, start):
  rows = query_rows(c, '''SELECT verb, noun, turn
                            FROM milestones
                           WHERE player = %s
                             AND start_time = %s
                             AND (verb = 'br.enter'
                                  AND (noun != 'Pan' OR milestone = 'entered Pandemonium.')
                                  OR verb = 'br.end'
                                  OR verb = 'br.exit'
                                  OR verb = 'rune'
                                  OR verb = 'orb')
                        ORDER BY turn''', name, start)

  def find_stone(verb,noun):
    for r in rows:
      if r[0] == verb and r[1] == noun:
        return r[2]
    return -1

  def count_runes(turn1, turn2):
    count = 0
    for r in rows:
      if r[0] == 'rune' and r[1] != 'abyssal':
        if r[2] >= turn1 and r[2] <= turn2:
          count += 1
    return count

  # Let's check a lot of things.
  # First, reaching the ends of branches. We don't need to check this in
  # rune or orb branches.
  for br in ['Lair','Orc','Elf','Crypt']:
    x = find_stone('br.enter',br)
    if x > -1:
      y = find_stone('br.end',br)
      z = find_stone('br.exit',br)
      if y == -1 or z < y:
        return 0
  # Next, getting runes.
  for br in ['Swamp','Snake','Shoals','Spider','Slime','Tomb',
             'Coc','Dis','Geh','Tar']:
    x = find_stone('br.enter',br)
    if x > -1:
      z = find_stone('br.exit',br)
      count = count_runes(x,z)
      if count == 0:
        return 0
  # Handle Vaults separately because it contains Tomb.
  x = find_stone('br.enter','Vaults')
  if x > -1:
    y = find_stone('rune','silver')
    z = find_stone('br.exit','Vaults')
    if y == -1 or z < y:
      return 0
  # Handle Pan separately also.
  pan_entrances = [r[2] for r in rows if r[0] == 'br.enter' and r[1] == 'Pan']
  if len(pan_entrances) > 0:
    count = 0
    for r in rows:
      if r[2] > pan_entrances[0]:
        if len(pan_entrances) == 1 or r[2] < pan_entrances[1]:
          if r[0] == 'rune' and r[1] in ['demonic','magical','glowing','fiery','dark']:
            count += 1
    if count < 5:
      return 0
  # Finally, check for the orb.
  y = find_stone('orb','orb')
  z = find_stone('br.exit','Zot')
  if z < y:
    return 0
  # Done checking for Ash banner II.
  # Now check for entering subbranches.
  # First, the subbranches of D have to be entered at some point in the game.
  for br in ['Lair','Orc','Vaults','Hell','Pan']:
    if find_stone('br.enter',br) == -1:
      return 2
  # Now check for guaranteed subbranches of other branches.
  for br in [['Lair','Slime'],['Orc','Elf'],['Vaults','Crypt'],['Crypt','Tomb'],['Hell','Coc'],['Hell','Dis'],['Hell','Geh'],['Hell','Tar']]:
    y = find_stone('br.enter',br[1])
    z = find_stone('br.exit',br[0])
    if z < y:
      return 2
  # Finally check for subbranches of Lair.
  z = find_stone('br.exit','Lair')
  count = 0
  for r in rows:
    if r[2] < z and r[0] == 'br.enter' and r[1] in ['Swamp','Snake','Shoals','Spider']:
      count += 1
  if count < 2:
    return 2
  # Congratulations, you made it this far...
  return 3

def check_ru_abandonment_game(c, name, start):
  champion_time = query_first_def(c, None, '''SELECT turn
                                      FROM milestones
                                     WHERE player = %s
                                       AND start_time = %s
                                       AND verb = 'god.maxpiety'
                                       AND noun = 'Ru'
                                  ORDER BY turn''', name, start)
  if not champion_time:
    return False
  abandon_time = query_first_def(c, None, '''SELECT turn
                                     FROM milestones
                                    WHERE player = %s
                                      AND start_time = %s
                                      AND verb = 'god.renounce'
                                      AND noun = 'Ru'
                                      AND turn >= %s
                                 ORDER BY turn''', name, start, champion_time)
  if not abandon_time:
    return False
  return not query_first_def(c, None, '''SELECT COUNT(*)
                                 FROM milestones
                                WHERE player = %s
                                  AND start_time = %s
                                  AND verb = 'br.enter'
                                  AND turn < %s
                                  AND ((noun = 'Orc') OR (noun = 'Vaults')
                                       OR (noun = 'Depths') OR (noun = 'Slime')
                                       OR (noun = 'Shoals') OR (noun = 'Snake')
                                       OR (noun = 'Spider') OR (noun = 'Swamp')
                                      ) ''', name, start, abandon_time)

################################################################################
# New (0.25) Tournament scoring queries begin here. Some will be cannibalized
# from old tournament scoring above.
################################################################################

###############################
# Individual Scoring Categories
###############################

def assign_nonrep_win(c, player, number):
  query_do(c, '''INSERT INTO players (name, nonrep_wins) VALUES (%s, %s)
                 ON DUPLICATE KEY UPDATE nonrep_wins = %s''',
                 player, number, number)

def first_win_order_query(limit = None):
  fields = logfile_fields('g.')
  query = Query("SELECT " + logfile_fields()
                + " FROM first_wins ORDER BY end_time")
  if limit:
    query.append(' LIMIT %d' % limit)

  return query

def first_win_order(c, limit = None):
  query = first_win_order_query(limit)
  return [ row_to_xdict(x) for x in query.rows(c) ]

def first_allrune_win_order_query(limit = None):
  query =  Query('SELECT ' + logfile_fields()
                 + ' FROM first_allrune_wins ORDER BY end_time')
  if limit:
    query.append(' LIMIT %d' % limit)

  return query

def first_allrune_win_order(c, limit = None):
  query = first_allrune_win_order_query(limit)
  return [ row_to_xdict(x) for x in query.rows(c) ]

def win_perc_order(c, limit = None):
  query = Query('''SELECT player, win_perc FROM player_win_perc
                   ORDER BY win_perc DESC''')
  if limit:
    query.append(' LIMIT %d' % limit)
  return query.rows(c)

def high_score_order(c, limit = None):
  query = Query("SELECT " + logfile_fields() + ''' FROM highest_scores
                   ORDER BY score DESC''')
  if limit:
    query.append(' LIMIT %d' % limit)

  return [ row_to_xdict(x) for x in query.rows(c) ]

def low_turncount_win_order(c, limit = None):
  fields = logfile_fields('g.')
  query = Query('''SELECT ''' + logfile_fields()
                + " FROM lowest_turncount_wins ORDER BY turn")
  if limit:
    query.append(' LIMIT %d' % limit)

  return [ row_to_xdict(x) for x in query.rows(c) ]

def fastest_win_order(c, limit = None):
  fields = logfile_fields('g.')
  query = Query('''SELECT ''' + logfile_fields()
                + ''' FROM fastest_wins ORDER BY duration''')
  if limit:
    query.append(' LIMIT %d' % limit)

  return [ row_to_xdict(x) for x in query.rows(c) ]

def low_xl_win_order(c, limit = None):
  fields = logfile_fields('g.')
  query = Query('''SELECT ''' + logfile_fields()
                + ''' FROM low_xl_nonhep_wins ORDER BY xl''')
  if limit:
    query.append(' LIMIT %d' % limit)

  return [ row_to_xdict(x) for x in query.rows(c) ]

def piety_order(c):
  return query_rows(c, "SELECT player, champion, won, piety"
                       +" FROM player_piety_score ORDER BY piety DESC")

def banner_order(c, limit = None):
  query = Query('''SELECT player, bscore, banners FROM player_banner_score
                   ORDER BY bscore DESC''')
  if limit:
    query.append(' LIMIT %d' % limit)
  return query.rows(c)

def exploration_order(c):
  return query_rows(c,'''SELECT player, score FROM player_exploration_score
                         ORDER BY score DESC''')

def harvest_order(c):
  return query_rows(c,'''SELECT player, score FROM player_harvest_score
                         ORDER BY score DESC''')

def zig_dive_order(c, limit = None):
  query = Query('''SELECT player, completed, deepest, 27 * completed + deepest FROM ziggurats
                   ORDER BY completed DESC, deepest DESC''')
  if limit:
    query.append(' LIMIT %d' % limit)
  return query.rows(c)

def combo_score_order(c, limit = None):
  query = Query('''SELECT player, total, combos, won_combos, sp_hs, cls_hs
                   FROM player_combo_score
                   ORDER BY total DESC, sp_hs DESC,
                            cls_hs DESC, won_combos DESC''')
  if limit:
    query.append(' LIMIT %d' % limit)
  return query.rows(c)

def get_nemelex_wins(c, how_many=None, player=None):
  query = Query("SELECT " + ",".join(LOG_FIELDS) +
                (""" FROM player_nem_scored_wins
                     WHERE nem_counts = 1 %s
                     ORDER BY end_time""" %
                 (player and 'AND player = %s' or '')))
  if player is not None:
    query.vappend(player)
  if how_many:
    query.append(" LIMIT %d" % how_many)
  return [ row_to_xdict(x) for x in query.rows(c) ]

def nemelex_order(c, limit=None):
  query = Query('''SELECT player, score
                   FROM player_nemelex_score GROUP BY player ORDER BY score DESC''')
  if limit:
    query.append(' LIMIT %d' % limit)
  return query.rows(c)

def update_streak(c, streak):
  json_data = json.dumps(streak, default = lambda o : o.__str__())
  query_do(c, '''INSERT INTO streaks
                      VALUES (%s, %s, %s, %s, %s)
                 ON DUPLICATE KEY UPDATE length = %s, streak_data = %s ''',
           streak['player'], streak['games'][0]['src'],
           streak['games'][0]['start_time'],
           streak['length'], json_data, streak['length'], json_data)

def streak_order(c, limit=None):
  query = Query('''SELECT s.player, s.src, s.start_time, s.length
                   FROM streaks AS s LEFT OUTER JOIN streaks AS s2
                   ON s.player = s2.player AND (s.length, s.start_time) < 
                   (s2.length, s2.start_time)
                   WHERE s2.start_time IS NULL ORDER BY s.length DESC''')
  if limit:
    query.append(' LIMIT %d' % limit)
  return query.rows(c)

def update_rank(c, rank_table, source_foreign_key, source_rank_order_clause,
    source_table, rank_table_key, rank_column):
    query_text = '''
    UPDATE
      {rank_table} AS t
      INNER JOIN (
        SELECT
          {source_foreign_key},
          DENSE_RANK() OVER(ORDER BY {source_rank_order_clause}) AS rk
        FROM
          {source_table}
        WHERE
          {source_foreign_key} IS NOT NULL
      ) AS r
      ON
        t.{rank_table_key} = r.{source_foreign_key}
      SET
        t.{rank_column} = r.rk
    '''.format(
        rank_table = rank_table,
        source_foreign_key = source_foreign_key,
        source_rank_order_clause=source_rank_order_clause,
        source_table=source_table,
        rank_table_key=rank_table_key,
        rank_column=rank_column,
    )
    query_do(c, query_text)
    return

def update_score(c, rank_table, source_foreign_key, source_rank_order_clause,
    source_table, rank_table_key, rank_column):
    query_text = '''
    UPDATE
      {rank_table} AS t
      INNER JOIN {source_table} AS r
      ON
        t.{rank_table_key} = r.{source_foreign_key}
      SET
        t.{rank_column} = r.{source_rank_order_clause}
    '''.format(
        rank_table = rank_table,
        source_foreign_key = source_foreign_key,
        source_rank_order_clause=source_rank_order_clause,
        source_table=source_table,
        rank_table_key=rank_table_key,
        rank_column=rank_column,
    )
    query_do(c, query_text)
    return

def update_all_player_ranks(c):
    for ic in INDIVIDUAL_CATEGORIES:
        if ic.source_table is not None and not ic.proportional:
            info("Updating player rank for %s", ic.name)
            update_rank(
                c,
                rank_table='players',
                source_foreign_key='player',
                source_rank_order_clause=ic.rank_order_clause,
                source_table=ic.source_table,
                rank_table_key='name',
                rank_column=ic.rank_column,
            )
        elif ic.source_table is not None:
            info("Updating player score for %s", ic.name)
            update_score(c,
                rank_table='players',
                source_foreign_key='player',
                source_rank_order_clause=ic.rank_order_clause,
                source_table=ic.source_table,
                rank_table_key='name',
                rank_column=ic.rank_column,
            )
    return

def update_clan_wins(c):
    query_do(c, '''UPDATE teams AS t INNER JOIN
                     (SELECT team_captain, LEAST(SUM(first_four),12) AS rk
                        FROM clan_combo_first_wins GROUP BY team_captain) AS r
                   ON t.owner = r.team_captain SET t.nonrep_wins = r.rk''')
    return

def update_all_clan_ranks(c):
    update_clan_wins(c)
    for cc in CLAN_CATEGORIES:
        if cc.source_table is not None and not cc.proportional:
            info("Updating clan rank for %s", cc.name)
            update_rank(
                c,
                rank_table='teams',
                source_foreign_key='team_captain',
                source_rank_order_clause=cc.rank_order_clause,
                source_table=cc.source_table,
                rank_table_key='owner',
                rank_column=cc.rank_column,
            )
        elif cc.source_table is not None:
            info("Updating clan score for %s", cc.name)
            update_score(c,
                rank_table='teams',
                source_foreign_key='team_captain',
                source_rank_order_clause=cc.rank_order_clause,
                source_table=cc.source_table,
                rank_table_key='owner',
                rank_column=cc.rank_column,
            )
    return

def score_term(cat):
    if cat.proportional:
        return "COALESCE( %5.1f * ( LEAST( %s, %5.1f ) / %5.1f ), 0.0 )" % (MAX_CATEGORY_SCORE,
                cat.rank_column, cat.max, cat.max)
    else:
        return "COALESCE( %5.1f / %s, 0.0 )" % (MAX_CATEGORY_SCORE,
                cat.rank_column)

def update_player_scores(c):
    SCOREFUNC = "CAST( (" + "+".join([ score_term(ic) for
        ic in INDIVIDUAL_CATEGORIES]) \
        + ") AS DECIMAL(7,0))";

    query_do(c, '''UPDATE players
                   SET score_full = ''' + SCOREFUNC)

def update_clan_scores(c):
    SCOREFUNC = "CAST( (" + "+".join([ score_term(cc) for
        cc in CLAN_CATEGORIES]) \
        + ") AS DECIMAL(7,0))";

    query_do(c, '''UPDATE teams SET total_score = ''' + SCOREFUNC)

def render_rank(n):
    if n is None:
        # return "&#x221E;" # ∞
        return "-"
    return n

def get_all_players(c):
  q = Query('''SELECT p.name, p.team_captain, t.name
                    FROM players p LEFT JOIN teams t
                      ON p.team_captain = t.owner
                    ORDER BY p.name''')
  rows = [ list(r) for r in q.rows(c) ]
  clean_rows = [ ]
  for r in rows:
    captain = r[1]
    clan_link = "" if captain is None else (
      crawl_utils.link_text(r[2], crawl_utils.clan_link(r[2], r[1])))
    player_link = crawl_utils.linked_text(r[0], crawl_utils.player_link)
    clean_rows.append([r[0], player_link, clan_link])

  return clean_rows

def get_all_clans(c):
  q = Query('''SELECT t.name, t.owner FROM teams t ORDER BY t.name''')
  rows = [ list(r) for r in q.rows(c) ]
  clean_rows = []
  for r in rows:
    clan_link = crawl_utils.link_text(r[0], crawl_utils.clan_link(r[0], r[1]))
    clean_rows.append([r[0], r[1], clan_link])
  return clean_rows

def get_all_player_ranks(c):
  q = Query('''SELECT p.name, p.team_captain, t.name, p.score_full, '''
               + ",".join([ 'p.' + ic.rank_column for ic in INDIVIDUAL_CATEGORIES ]) +
               ''' FROM players p
               LEFT JOIN teams t
               ON p.team_captain = t.owner
               ORDER BY p.score_full DESC, p.name''')
  rows = [ list(r) for r in q.rows(c) ]
  clean_rows = [ ]
  for r in rows:
    captain = r[1]
    r = r[0:1] + r[2:]
    if captain is None:
      r[1] = ''
    else:
      clan_info = get_clan_info(c, captain)
      if clan_info is None:
        r[1] = ''
      else:
        clan_page = clan_info[2]
        r[1] = crawl_utils.link_text(r[1], crawl_utils.clan_link(r[1], captain))
    r = [ render_rank(n) for n in r ]
    clean_rows.append(r)
  return clean_rows

def get_all_clan_ranks(c, pretty=True, limit=None):
  q = Query('''SELECT name, owner, total_score, '''
               + ",".join([ cc.rank_column for cc in CLAN_CATEGORIES]) +
            ''' FROM teams
               ORDER BY total_score DESC, name''')

  rows = [ list(r) for r in q.rows(c) ]
  clean_rows = [ ]
  for r in rows:
      captain = r[1]
      if pretty:
        r[0] = crawl_utils.link_text(r[0], crawl_utils.clan_link(r[0], captain))
        r[1] = crawl_utils.clan_affiliation(captain, get_clan_info(c, captain),
                False)
        clean_rows.append( [render_rank(n) for n in r] )
      else:
        clean_rows.append(r)
  if limit is not None:
    clean_rows = clean_rows[:limit]
  return clean_rows
