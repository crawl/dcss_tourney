import MySQLdb
import re
import os

import logging
from logging import debug, info, warn, error

""" Other people working on scoring: You might want to take a look at
converting all the methods to look and poke at the db that I wrote to
use cursors instead of the db handle directly.

Also, below is my suggestion for a way for dispatch to work, stubbed
out.  Feel free to do something completely different if I'm cramping
your style--I expect other people have plenty more time to work on this than
I.  We may also want these to just dispatch to passed-in functions--we
could keep the scoring functions for different things in outline.py or
something.

--violet
"""

class CrawlEventListener(object):
  """The way this is intended to work is that on receipt of an event
  ... we shoot the messenger. :P"""
  def score_event(self, cursor, dict):
    """Return a list of query strings to execute to modify the base scores in the db based on this event"""
    raise Exception, "Please subclass me!"
  def insert_event(self, cursor, dict):
    """Make the database reflect that this event happened."""
    raise Exception, "Please subclass me!"
  def execute(self, cursor, dict):
    """Score the event, start a transaction, execute the score change queries, insert the event, close the transaction"""
    raise Exception, "Please implement me in this, the superclass"

TOURNAMENT_DB = 'tournament'
LOGS = [ 'cao-logfile-0.4',
         'cdo-logfile-0.4' ]
MILESTONES = [ 'cao-milestones-0.4' ]
COMMIT_INTERVAL = 3000

def connect_db():
  connection = MySQLdb.connect(host='localhost',
                               user='crawl',
                               db=TOURNAMENT_DB)
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

def xlog_dict(logline):
  d = parse_logline(logline)
  # Fixup rune madness where one or the other is set, but not both.
  if d.get('nrune') is not None or d.get('urune') is not None:
    d['nrune'] = d.get('nrune') or d.get('urune')
    d['urune'] = d.get('urune') or d.get('nrune')
  return d

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
R_GHOST_NAME = re.compile(r"^(.*)'s? ghost")
R_MILESTONE_GHOST_NAME = re.compile(r"the ghost of (.*) the ")
R_KILL_UNIQUE = re.compile(r'^killed (.*)\.$')
R_RUNE = re.compile(r"found an? (.*) rune")

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

class Query:
  def __init__(self, qstring, *values):
    self.query = qstring
    self.values = values

  def append(self, qseg, *values):
    self.query += qseg
    self.values += values

  def vappend(self, *values):
    self.values += values

  def execute(self, cursor):
    """Executes query on the supplied cursor."""
    self.query = self.query.strip()
    if not self.query.endswith(';'):
      self.query += ';'
    cursor.execute(self.query, self.values)

  def row(self, cursor):
    """Executes query and returns the first row tuple, or None if there are no
    rows."""
    self.execute(cursor)
    return cursor.fetchone()

  def rows(self, cursor):
    self.execute(cursor)
    return cursor.fetchall()

  def count(self, cursor, msg=None, exc=Exception):
    """Executes a SELECT COUNT(foo) query and returns the count. If there is
    not at least one row, raises an exception."""
    self.execute(cursor)
    row = cursor.fetchone()
    if row is None:
      raise exc, (msg or "No rows returned for %s" % self.query)
    return row[0]

  first = count


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

def query_do(cursor, query, *values):
  Query(query, *values).execute(cursor)

def query_first(cursor, query, *values):
  return Query(query, *values).first(cursor)

def query_row(cursor, query, *values):
  return Query(query, *values).row(cursor)

def query_rows(cursor, query, *values):
  return Query(query, *values).rows(cursor)

def apply_dbtypes(game):
  """Given an xlogline dictionary, replaces all values with munged values
  that can be inserted directly into a db table. Keys that are not recognized
  (i.e. not in dbfield_to_sqltype) are ignored."""
  new_hash = { }
  for key, value in game.items():
    if LOGLINE_TO_DBFIELD.has_key(key):
      new_hash[key] = dbfield_to_sqltype[LOGLINE_TO_DBFIELD[key]].to_sql(value)
    else:
      new_hash[key] = value
  return new_hash

def make_games_insert_query(logdict, filename, offset):
  fields = ["source_file", "source_file_offset"]
  values = [filename, offset]

  dbfields = apply_dbtypes(logdict)

  for logkey, sqlkey in LOG_DB_MAPPINGS:
    if dbfields.has_key(logkey):
      fields.append(sqlkey)
      values.append(dbfields[logkey])

  return Query('INSERT INTO games (%s) VALUES (%s);' %
               (",".join(fields), ",".join([ "%s" for v in values])),
               *values)

def insert_logline(cursor, logdict, filename, offset):
  query = make_games_insert_query(logdict, filename, offset)
  try:
    query.execute(cursor)
  except Exception, e:
    error("Error inserting logline %s (query: %s [%s]): %s"
          % (logdict, query.query, query.values, e))
    raise

def dbfile_offset(cursor, table, filename):
  """Given a db cursor and filename, returns the offset of the last
  logline from that file that was entered in the db."""
  return query_first(cursor,
                     ('SELECT MAX(source_file_offset) FROM %s ' % table) + \
                       'WHERE source_file = %s',
                     filename) or -1

def logfile_offset(cursor, filename):
  return dbfile_offset(cursor, 'games', filename)

def milestone_offset(cursor, filename):
  return dbfile_offset(cursor, 'milestone_bookmark', filename)

def update_db_bookmark(cursor, table, filename, offset):
  cursor.execute('INSERT INTO ' + table + \
                   ' (source_file, source_file_offset) VALUES (%s, %s) ' + \
                   'ON DUPLICATE KEY UPDATE source_file_offset = %s',
                 [ filename, offset, offset ])

def update_milestone_bookmark(cursor, filename, offset):
  return update_db_bookmark(cursor, 'milestone_bookmark', filename, offset)

def xlog_seek(filename, filehandle, offset):
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

def read_offset_lines(handle, offset=None):
  if offset is not None:
    handle.seek(offset)
  while True:
    offset = handle.tell()
    line = handle.readline()
    if not line or not line.endswith("\n"):
      line = None
    yield offset, line

def tail_file_lines(filename, filehandle, offset, line_op):
  """Given a filename and filehandle, seeks to the supplied offset and reads
  lines, calling the supplied function with the offset and line. Returns the
  offset that is just past the last newline-terminated line."""
  inserted = 0
  for off, line in read_offset_lines(filehandle, offset):
    offset = off
    if line is None:
      break

    line_op(off, line)

    inserted += 1
    if inserted % 5000 == 0:
      info("Inserted %d rows from %s." % (inserted, filename))

  if inserted > 0:
    info("Inserted %d rows." % inserted)

  return offset

def extract_ghost_name(killer):
  return R_GHOST_NAME.findall(killer)[0]

def extract_milestone_ghost_name(milestone):
  return R_MILESTONE_GHOST_NAME.findall(milestone)[0]

def extract_rune(milestone):
  return R_RUNE.findall(milestone)[0]

def record_ghost_kill(cursor, game):
  """Given a game where the character was slain by a ghost, adds an entry in
  the kills_by_ghosts table."""
  game = apply_dbtypes(game)
  query_do(cursor,
           '''INSERT INTO kills_by_ghosts
              (killed_player, killed_start_time, killer) VALUES
              (%s, %s, %s);''',
           game['name'], game['start'], extract_ghost_name(game['killer']))

def tail_file_into_games(cursor, filename, filehandle, offset=None):
  """Given a logfile handle, seeks to the supplied offset if any, and
  writes all available records into the games table. Returns the fileoffset
  at the point immediately past the last log entry read."""

  def process_logline(offset, line):
    d = xlog_dict(line.strip())
    killer = d.get('killer') or ''
    ghost_kill = R_GHOST_NAME.search(killer)
    cursor.execute('BEGIN;')
    try:
      insert_logline(cursor, d, filename, offset)
      if ghost_kill:
        record_ghost_kill(cursor, d)
      cursor.execute('COMMIT;')
    except:
      cursor.execute('ROLLBACK;')
      raise

  return tail_file_lines(filename, filehandle, offset, process_logline)

def tail_milestones(cursor, filename, filehandle, offset=None):
  def process_milestone(offset, line):
    add_milestone_record(cursor, filename, filehandle, offset, line)

  return tail_file_lines(filename, filehandle, offset, process_milestone)

def extract_unique_name(kill_message):
  return R_KILL_UNIQUE.findall(kill_message)[0]

def add_unique_milestone(cursor, game):
  if not game['milestone'].startswith('banished '):
    query_do(cursor,
             '''INSERT INTO kills_of_uniques (player, kill_time, monster)
                VALUES (%s, %s, %s);''',
             game['name'],
             datetime.to_sql(game['time']),
             extract_unique_name(game['milestone']))

def add_ghost_milestone(cursor, game):
  if not game['milestone'].startswith('banished '):
    query_do(cursor,
             '''INSERT INTO kills_of_ghosts (player, start_time, ghost)
                VALUES (%s, %s, %s);''',
             game['name'], datetime.to_sql(game['time']),
             extract_milestone_ghost_name(game['milestone']))

def add_rune_milestone(cursor, game):
  query_do(cursor,
           '''INSERT INTO rune_finds (player, start_time, rune)
              VALUES (%s, %s, %s);''',
           game['name'], datetime.to_sql(game['time']),
           extract_rune(game['milestone']))

MILESTONE_HANDLERS = {
  'unique' : add_unique_milestone,
  'ghost' : add_ghost_milestone,
  'rune' : add_rune_milestone
}

def add_milestone_record(c, filename, handle, offset, line):
  d = apply_dbtypes(parse_logline(line.strip()))

  # Start a transaction to ensure that we don't part-update tables.
  c.execute('BEGIN;')
  try:
    update_milestone_bookmark(c, filename, offset)
    handler = MILESTONE_HANDLERS.get(d['type'])
    if handler:
      handler(c, d)
    c.execute('COMMIT;')
  except:
    c.execute('ROLLBACK;')
    raise

def read_file_into_games(db, filename, filehandle):
  """Take a database with an open connection, and a name of a file, and
  slurp the entire contents of the file into the games table of the database.
  This is pretty much only for testing."""
  cursor = db.cursor()
  xlog_seek(filename, filehandle, logfile_offset(cursor, filename))
  try:
    return tail_file_into_games(cursor, filename, filehandle)
  finally:
    cursor.close()

def read_milestone_file(db, filename, filehandle):
  """Takes a db with an open connection, the name of a milestone file and
  an open filehandle into the file and writes the milestones into the
  appropriate db tables. Also takes care to resume where it left off if
  interrupted."""
  cursor = db.cursor()
  xlog_seek(filename, filehandle, milestone_offset(cursor, filename))
  try:
    return tail_milestones(cursor, filename, filehandle)
  finally:
    cursor.close()

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  print "Populating db (one-off) with logfiles and milestones. " + \
      "Running the taildb.py daemon is preferred."
  db = connect_db()

  def proc_file(fn, filename):
    info("Updating db with %s" % filename)
    try:
      f = open(filename)
      try:
        fn(db, filename, f)
      finally:
        f.close()
    except IOError:
      warn("Error reading %s, skipping it." % log)

  for log in LOGS:
    proc_file(read_file_into_games, log)

  for milestone in MILESTONES:
    proc_file(read_milestone_file, milestone)
