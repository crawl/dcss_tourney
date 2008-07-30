import MySQLdb
import re

import logging
from logging import debug, info, warn, error

TOURNAMENT_DB = 'tournament'
LOGS = [ 'cao-logfile', 'cdo-logfile' ]
MILESTONES = [ 'cao-milestones', 'cdo-milestones' ]
COMMIT_INTERVAL = 3000

logging.basicConfig(level=logging.DEBUG)

def connect_db():
  connection = MySQLdb.connect(host='localhost', user='crawl',
                               db='tournament')
  return connection

def parse_logline(logline):
  """This function takes a logfile line, which is mostly separated by colons,
  and parses it into a dictionary (which everyone except Python calls a hash).
  Because the Crawl developers are insane, a double-colon is an escaped colon,
  and so we have to be careful not to split the logfile on locations like
  D:7 and such. It also works on milestones and whereis."""
  # This is taken from Henzell. Yay Henzell!
  if not logline:
    raise Exception, "no logline"
  if logline[0] == ':' or (logline[-1] == ':' and not logline[-2] == ':'):
    raise Exception,  "starts with colon"
  if '\n' in logline:
    raise Exception, "more than one line"
  logline = logline.replace("::", "\n")
  details = dict([(item[:item.index('=')], item[item.index('=') + 1:]) for item in logline.split(':')])
  for key in details:
    details[key] = details[key].replace("\n", ":")
  return details

# The mappings in order so that we can generate our db queries with all the
# fields in order and generally debug things more easily.
LOG_DB_MAPPINGS = [
    [ 'v', 'version' ],
    [ 'lv', 'lv' ],
    [ 'name', 'player' ],
    [ 'uid', 'uid' ],
    [ 'race', 'race' ],
    [ 'cls', 'class' ],
    [ 'char', 'charabbrev' ],
    [ 'xl', 'xl' ],
    [ 'sk', 'skill' ],
    [ 'sklev', 'sk_lev' ],
    [ 'title', 'title' ],
    [ 'place', 'place' ],
    [ 'br', 'branch' ],
    [ 'lvl', 'lvl' ],
    [ 'ltyp', 'ltyp' ],
    [ 'hp', 'hp' ],
    [ 'mhp', 'maxhp' ],
    [ 'mmhp', 'maxmaxhp' ],
    [ 'str', 'strength' ],
    [ 'int', 'intellegence' ],
    [ 'dex', 'dexterity' ],
    [ 'god', 'god' ],
    [ 'start', 'start_time' ],
    [ 'dur', 'duration' ],
    [ 'turn', 'turn' ],
    [ 'sc', 'score' ],
    [ 'ktyp', 'killertype' ],
    [ 'killer', 'killer' ],
    [ 'dam', 'damage' ],
    [ 'piety', 'piety' ],
    [ 'pen', 'penitence' ],
    [ 'end', 'end_time' ],
    [ 'tmsg', 'terse_msg' ],
    [ 'vmsg', 'verb_msg' ],
    [ 'kaux', 'kaux' ],
    [ 'nrune', 'nrune' ],
    [ 'urune', 'runes' ] ]

LOGLINE_TO_DBFIELD = dict(LOG_DB_MAPPINGS)
R_MONTH_FIX = re.compile(r'^(\d{4})(\d{2})(.*)')

class SqlType:
  def __init__(self, str_to_sql):
    #print str_to_sql('1')
    self.str_to_sql = str_to_sql

  def to_sql(self, string):
    return (self.str_to_sql)(string)

def fix_crawl_date(date):
  def inc_month(match):
    return "%s%02d%s" % (match.group(1), 1 + int(match.group(2)),
                         match.group(3))
  return R_MONTH_FIX.sub(inc_month, date)

char = SqlType(lambda x: x)
#remove the trailing 'D'/'S', fixup date
datetime = SqlType(lambda x: fix_crawl_date(x[0:-1]))
bigint = SqlType(lambda x: int(x))
sql_int = bigint
varchar = char

dbfield_to_sqltype = {
	'player':char,
	'start_time':datetime,
	'score':bigint,
	'race':char,
	'class':char,
	'version':char,
	'lv':char,
	'uid':sql_int,
	'charabbrev':char,
	'xl':sql_int,
	'skill':char,
	'sk_lev':sql_int,
	'title':varchar,
	'place':char,
	'branch':char,
	'lvl':sql_int,
	'ltyp':char,
	'hp':sql_int,
	'maxhp':sql_int,
 	'maxmaxhp':sql_int,
	'strength':sql_int,
	'intellegence':sql_int,
	'dexterity':sql_int,
	'god':char,
	'duration':sql_int,
	'turn':bigint,
	'runes':sql_int,
	'killertype':char,
	'killer':char,
        'kaux':char,
	'damage':sql_int,
	'piety':sql_int,
        'penitence':sql_int,
	'end_time':datetime,
	'terse_msg':varchar,
	'verb_msg':varchar,
        'nrune':sql_int,
	}

def make_games_insert_query(logdict, filename, offset):
  fields = ["source_file", "source_file_offset"]
  values = [filename, offset]

  for logkey, sqlkey in LOG_DB_MAPPINGS:
    if logdict.has_key(logkey):
      type = dbfield_to_sqltype[sqlkey]
      fields.append(sqlkey)
      values.append(type.to_sql(logdict[logkey]))

  return ('INSERT INTO games (%s) VALUES (%s);' %
            (",".join(fields), ",".join([ "%s" for v in values])),
          values)

def count_wins(db, player, character_race=None, character_class=None):
  """Return the number wins recorded for the given player, optionally with
     a specific race, class, or both"""
  query_string = "select count(start_time) from games where killertype='winning' && player='%s' "
  query_string = query_string % player
  if (character_race):
    query_string += """&& race='%s' """ % (character_race,)
  if (character_class):
    query_string += """&& class='%s' """ % (character_class,)
  query_string += ";"
  db.query(query_string)
  res = db.store_result()
  ((count,),) = res.fetch_row()
  return int(count)

def player_exists(db, name):
  """Return true if the player exists in the player table"""
  query_string = """select name from players where name='%s';""" % name
  db.query(query_string)
  res = db.store_result()
  rows = res.fetch_row()
  return len(rows) != 0

def add_player(db, name):
  """Add the given player with no score yet"""
  query_string = """insert into players (name, score_base, team_score_base) values ('%s', 0, 0);""" % name
  db.query(query_string)

def get_player_base_score(db, name):
  """Return the unchanging part of a player's score"""
  query_string = """select score_base from players where name='%s';""" % name
  db.query(query_string)
  res = db.store_result()
  if res.num_rows() != 1:
    raise Exception, "Player not found: %s" % name
  ((score,),) = res.fetch_row()
  return int(score)

def get_player_base_team_score(db, name):
  """Return the unchanging part of a player's team score contribution"""
  query_string = """select team_score_base from players where name='%s';""" % name
  db.query(query_string)
  res = db.store_result()
  if res.num_rows() != 1:
    raise Exception, "Player not found: %s" % name
  ((score,),) = res.fetch_row()
  return int(score)

def assign_points(db, name, points):
  """Add points to a player's points in the db"""
  prev = get_player_base_score(db, name)
  query_string = """update players set score_base=%s where name='%s';""" % (prev+points, name)
  db.query(query_string)

def assign_team_points(db, name, points):
  """Add points to a players team in the db.  The name refers to the player, not the team"""
  prev = get_player_base_team_score(db, name)
  query_string = """update players set team_score_base=%s where name='%s';""" % (prev+points, name)
  db.query(query_string)

def insert_logline(cursor, logdict, filename, offset):
  query, values = make_games_insert_query(logdict, filename, offset)
  try:
    cursor.execute(query, values)
  except Exception, e:
    error("Error inserting logline %s (query: %s [%s]): %s"
          % (logdict, query, values, e))
    raise

def logfile_offset(cursor, filename):
  """Given a db cursor and filename, returns the offset of the last
  logline from that file that was entered in the db."""

  query = '''SELECT MAX(source_file_offset) FROM games
             WHERE source_file = %s'''
  cursor.execute(query, filename)
  offset = cursor.fetchone()[0]
  return offset or -1

def logfile_seek(filename, filehandle, offset):
  """Given a logfile handle and the offset of the last logfile entry inserted
  in the db, seeks to the last entry and reads past it, positioning the
  read pointer at the start of the first new logfile entry."""

  info("Seeking to offset %d in logfile %s" % (offset, filename))
  if offset == -1:
    filehandle.seek(0)
  else:
    filehandle.seek(offset > 0 and offset or (offset - 1))
    # Sanity-check: the byte immediately preceding this must be "\n".
    if offset > 0:
      filehandle.seek(offset - 1)
      if filehandle.read(1) != '\n':
        raise IOError("%s: Offset %d is not preceded by newline."
                      % (filename, offset))
    else:
      filehandle.seek(offset)
    # Discard one line - the last line added to the db.
    filehandle.readline()

def tail_file_into_games(cursor, filename, filehandle, offset=None):
  """Given a logfile handle, seeks to the supplied offset if any, and
  writes all available records into the games table. Returns the fileoffset
  at the point immediately past the last log entry read."""

  if offset:
    filehandle.seek(offset)

  inserted = 0
  while True:
    offset = filehandle.tell()
    line = filehandle.readline()
    if not line or not line.endswith("\n"):
      break
    d = parse_logline(line.strip())
    insert_logline(cursor, d, filename, offset)
    inserted += 1
    if inserted % 5000 == 0:
      print("Inserted %d rows." % inserted)

  if inserted > 0:
    info("Inserted %d rows." % inserted)

  return offset

def read_file_into_games(db, filename, filehandle):
  """Take a database with an open connection, and a name of a file, and
  slurp the entire contents of the file into the games table of the database.
  This is pretty much only for testing."""
  cursor = db.cursor()
  logfile_seek(filename, filehandle, logfile_offset(cursor, filename))
  try:
    return tail_file_into_games(cursor, filename, filehandle)
  finally:
    cursor.close()

if __name__ == '__main__':
  db = connect_db()
  for log in LOGS:
    info("Updating db with %s" % log)
    try:
      f = open(log)
      try:
        read_file_into_games(db, log, f)
      finally:
        f.close()
    except IOError:
      warn("Error reading %s, skipping it." % log)
