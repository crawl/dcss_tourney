import MySQLdb
import re
import os
import datetime
import os.path
import crawl_utils

import logging
from logging import debug, info, warn, error

import ConfigParser
import imp
import sys

from test_data import USE_TEST, TEST_YEAR, TEST_VERSION, TEST_START_TIME, TEST_END_TIME, TEST_HARE_START_TIME, TEST_LOGS, TEST_MILESTONES, TEST_CLAN_DEADLINE

T_YEAR = TEST_YEAR or '2018'
T_VERSION = TEST_VERSION or '0.21'

# Start and end of the tournament, UTC.
START_TIME = TEST_START_TIME or (T_YEAR + '01052000')
END_TIME   = TEST_END_TIME or (T_YEAR + '01212000')

# Deadline for forming teams.
CLAN_DEADLINE = (TEST_CLAN_DEADLINE or
                datetime.datetime(2018, 1, 12, 23))

DATE_FORMAT = '%Y%m%d%H%M'

GAME_VERSION = T_VERSION

HARE_START_TIME = TEST_HARE_START_TIME or (T_YEAR + '01202000') # one day before tourney end

CAO = 'http://crawl.akrasiac.org/'
CBRO = 'http://crawl.berotato.org/crawl/'
CDO = 'http://crawl.develz.org/'
CJR = 'https://crawl.jorgrun.rocks/'
CPO = 'https://crawl.project357.org/'
CUE = 'https://underhound.eu/crawl/'
CWZ = 'https://webzook.net/soup/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

#CKR = 'http://kr.dobrazupa.org/'
#RHF = 'http://rl.heh.fi/'

# Log and milestone files. A tuple indicates a remote file with t[1]
# being the URL to wget -c from.

LOGS = TEST_LOGS or [
         ('cao-logfile-0.21', CAO + 'logfile21'),
         ('cbro-logfile-0.21', CBRO + 'meta/0.21/logfile'),
         ('cdo-logfile-0.21', CDO + 'allgames-0.21.txt'),
         ('cjr-logfile-0.21', CJR + 'meta/0.21/logfile'),
         ('cpo-logfile-0.21', CPO + 'dcss-logfiles-0.21'),
         ('cue-logfile-0.21', CUE + 'meta/0.21/logfile'),
         ('cwz-logfile-0.21', CWZ + '0.21/logfile'),
         ('cxc-logfile-0.21', CXC + 'meta/0.21/logfile'),
         ('lld-logfile-0.21', LLD + 'mirror/meta/0.21/logfile'),
  ]

MILESTONES = TEST_MILESTONES or [
         ('cao-milestones-0.21', CAO + 'milestones21'),
         ('cbro-milestones-0.21', CBRO + 'meta/0.21/milestones'),
         ('cdo-milestones-0.21', CDO + 'milestones-0.21.txt'),
         ('cjr-milestones-0.21', CJR + 'meta/0.21/milestones'),
         ('cpo-milestones-0.21', CPO + 'dcss-milestones-0.21'),
         ('cue-milestones-0.21', CUE + 'meta/0.21/milestones'),
         ('cwz-milestones-0.21', CWZ + '0.21/milestones'),
         ('cxc-milestones-0.21', CXC + 'meta/0.21/milestones'),
         ('lld-milestones-0.21', LLD + 'mirror/meta/0.21/milestones'),
  ]

BLACKLIST_FILE = 'blacklist.txt'
EXTENSION_FILE = 'modules.ext'
TOURNAMENT_DB = 'tournament'
COMMIT_INTERVAL = 3000
# These rcfiles need to be updated from the servers every few hours.
CRAWLRC_DIRECTORY_LIST = ['rcfiles-cao/','rcfiles-cbro/','rcfiles-cdo/', 'rcfiles-cjr/', 'rcfiles-cpo/','rcfiles-cue/','rcfiles-cwz/','rcfiles-cxc/','rcfiles-lld/']

LISTENERS = [ ]
TIMERS = [ ]

def support_mysql57(c):
    c.execute('SELECT @@SESSION.sql_mode')
    modes = c.fetchone()[0]
    modes = modes.split(',')
    if 'ONLY_FULL_GROUP_BY' in modes:
        modes = [m for m in modes if m != 'ONLY_FULL_GROUP_BY']
        c.execute("SET SESSION sql_mode = '%s'" % ','.join(modes))

class Blacklist(object):
  def __init__(self, filename):
    self.filename = filename
    if os.path.exists(filename):
      info("Loading blacklist from " + filename)
      self.load_blacklist()

  def load_blacklist(self):
    fh = open(self.filename)
    lines = fh.readlines()
    fh.close()
    self.blacklist = [apply_dbtypes(parse_logline(x.strip()))
                      for x in lines if x.strip()]

  def is_blacklisted(self, game):
    for b in self.blacklist:
      if xlog_match(b, game):
        return True
    return False

class CrawlEventListener(object):
  """The way this is intended to work is that on receipt of an event
  ... we shoot the messenger. :P"""
  def initialize(self, db):
    """Called before any processing, do your initialization here."""
    pass
  def cleanup(self, db):
    """Called after we're done processing, do cleanup here."""
    pass
  def logfile_event(self, cursor, logdict):
    """Called for each logfile record. cursor will be in a transaction."""
    pass
  def milestone_event(self, cursor, mdict):
    """Called for each milestone record. cursor will be in a transaction."""
    pass

class CrawlCleanupListener (CrawlEventListener):
  def __init__(self, fn):
    self.fn = fn

  def cleanup(self, db):
    c = db.cursor()
    support_mysql57(c)
    try:
      self.fn(c)
    finally:
      c.close()

class CrawlTimerListener:
  def __init__(self, fn=None):
    self.fn = fn

  def run(self, cursor, elapsed_time):
    if self.fn:
      self.fn(cursor)

class CrawlTimerState:
  def __init__(self, interval, listener):
    self.listener = listener
    self.interval = interval
    # Fire the first event immediately.
    self.target   = 0

  def run(self, cursor, elapsed):
    if self.target <= elapsed:
      self.listener.run(cursor, elapsed)
      self.target = elapsed + self.interval

#########################################################################
# xlogfile classes. xlogfiles are a colon-separated-field,
# newline-terminated-record key=val format. Colons in values are
# escaped by doubling. Originally created by Eidolos for NetHack logs
# on n.a.o, and adopted by Crawl as well.

# These classes merely read lines from the logfile, and do not parse them.

class Xlogline:
  """A dictionary from an Xlogfile, along with information about where and
  when it came from."""
  def __init__(self, owner, filename, offset, time, xdict, processor):
    self.owner = owner
    self.filename = filename
    self.offset = offset
    self.time = time
    if not time:
      raise Exception, \
          "Xlogline time missing from %s:%d: %s" % (filename, offset, xdict)
    self.xdict = xdict
    self.processor = processor

  def __cmp__(self, other):
    ltime = self.time
    rtime = other.time
    # Descending time sort order, so that later dates go first.
    if ltime > rtime:
      return -1
    elif ltime < rtime:
      return 1
    else:
      return 0

  def process(self, cursor):
    try:
      self.processor(cursor, self.filename, self.offset, self.xdict)
    except:
      sys.stderr.write("Error processing: " + xlog_str(self.xdict) + "\n")
      raise

class Xlogfile:
  def __init__(self, filename, tell_op, proc_op, blacklist=None):
    if isinstance(filename, tuple):
      self.local = False
      self.filename = filename[0]
      self.url = filename[1]
    else:
      self.local = True
      self.filename = filename
    self.handle = None
    self.offset = None
    self.tell_op = tell_op
    self.proc_op = proc_op
    self.size  = None
    self.blacklist = blacklist

  def reinit(self):
    """Reinitialize for a further read from this file."""
    # If this is a local file, take a snapshot of the file size here.
    # We will not read past this point. This is important because local
    # files grow constantly, whereas remote files grow only when we pull
    # them from the remote server, so we should not read past the point
    # in the local file corresponding to the point where we pulled from the
    # remote server.
    if self.local:
      self.size = os.path.getsize(self.filename)
    else:
      self.fetch_remote()

  def fetch_remote(self):
    info("Fetching remote %s to %s with wget -c" % (self.url, self.filename))
    res = os.system("wget -q -c --no-check-certificate %s -O %s" % (self.url, self.filename))
    if res != 0:
      raise IOError, "Failed to fetch %s with wget" % self.url

  def _open(self):
    try:
      self.handle = open(self.filename)
    except:
      warn("Cannot open %s" % self.filename)
      pass

  def have_handle(self):
    if self.handle:
      return True
    self._open()
    return self.handle

  def apply_blacklist(self, xdict):
    # Blacklisted games are mauled here:
    xdict['ktyp'] = 'blacklist'
    xdict['place'] = 'D:1'
    xdict['xl'] = 1
    xdict['lvl'] = 1
    xdict['tmsg'] = 'was blacklisted.'
    xdict['vmsg'] = 'was blacklisted.'

  def line(self, cursor):
    if not self.have_handle():
      return

    while True:
      if not self.offset:
        xlog_seek(self.filename, self.handle,
                  self.tell_op(cursor, self.filename))
        self.offset = self.handle.tell()

      # Don't read beyond the last snapshot size for local files.
      if self.local and self.offset >= self.size:
        return None

      line_offset = self.offset
      line = self.handle.readline()
      newoffset = self.handle.tell()
      if not line or not line.endswith("\n") or \
            (self.local and newoffset > self.size):
        # Reset to last read
        self.handle.seek(self.offset)
        return None

      self.offset = newoffset
      # If this is a blank line, advance the offset and keep reading.
      if not line.strip():
        continue

      # Also ignore bad lines caused by certain felid death milestones in 0.8-a.
      if line.startswith("             ..."):
        continue

      # bad logfile lines in cdo 0.16
      # I'm too tired to write a better check right now,
      # this should be replaced with something more specific
      if not line.startswith("v"):
        info(line)
        continue

      try:
        xdict = apply_dbtypes( xlog_dict(line) )
        if self.blacklist and self.blacklist.is_blacklisted(xdict):
          self.apply_blacklist(xdict)
      except:
        sys.stderr.write("Error processing line: " + line + "\n")
        raise

      if xdict['char'][:2] in ['Dj','LO','SE'] or xdict['char'][2:] in ['Pr']:
        continue

      xline = Xlogline( self, self.filename, line_offset,
                        xdict.get('end') or xdict.get('time'),
                        xdict, self.proc_op )
      return xline

class Logfile (Xlogfile):
  def __init__(self, filename, blacklist):
    Xlogfile.__init__(self, filename, logfile_offset, process_log, blacklist)

class MilestoneFile (Xlogfile):
  def __init__(self, filename):
    Xlogfile.__init__(self, filename, milestone_offset, add_milestone_record)

class MasterXlogReader:
  """Given a list of Xlogfile objects, calls the process operation on the oldest
  line from all the logfiles, and keeps doing this until all lines have been
  processed in chronological order."""
  def __init__(self, xlogs):
    self.xlogs = xlogs

  def reinit(self):
    for x in self.xlogs:
      x.reinit()

  def tail_all(self, cursor):
    self.reinit()
    lines = [ line for line in [ x.line(cursor) for x in self.xlogs ]
              if line ]

    proc = 0
    while lines:
      # Sort dates in descending order.
      lines.sort()
      # And pick the oldest.
      oldest = lines.pop()
      # Grab a replacement for the one we're going to read from the same file:
      newline = oldest.owner.line(cursor)
      if newline:
        lines.append(newline)
      # And process the line
      oldest.process(cursor)
      proc += 1
      if proc % 3000 == 0:
        info("Processed %d lines." % proc)
    if proc > 0:
      info("Done processing %d lines." % proc)

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
  details = dict([(item[:item.index('=')], item[item.index('=') + 1:])
                  for item in logline.split(':')])
  for key in details:
    details[key] = details[key].replace("\n", ":")
  return details

def xlog_set_killer_group(d):
  killer = d.get('killer')
  if not killer:
    ktyp = d.get('ktyp')
    if ktyp:
      d['kgroup'] = ktyp
    return

  m = R_GHOST_NAME.search(killer)
  if m:
    d['kgroup'] = 'player ghost'
    return

  m = R_HYDRA.search(killer)
  if m:
    d['kgroup'] = 'hydra'
    return

  d['kgroup'] = killer


def strip_unique_qualifier(x):
  if 'Lernaean' in x:
    return 'the Lernaean hydra'
  if 'Royal Jelly' in x:
    return 'the royal jelly'
  if 'Enchantress' in x:
    return 'the Enchantress'
  if 'Serpent of Hell' in x:
    return 'the Serpent of Hell'
  if ',' in x:
    p = x.index(',')
    return x[:p]
  if ' the ' in x:
    p = x.index(' the ')
    return x[:p]
  return x

def xlog_milestone_fixup(d):
  for field in [x for x in ['uid'] if d.has_key(x)]:
    del d[field]
  if not d.get('milestone'):
    d['milestone'] = ' '
  verb = d['type']
  milestone = d['milestone']
  noun = None

  if verb == 'unique':
    verb = 'uniq'

  if verb == 'enter':
    verb = 'br.enter'

  if verb == 'uniq':
    match = R_MILE_UNIQ.findall(milestone)
    if match[0][0] == 'banished':
      verb = 'uniq.ban'
    elif match[0][0] == 'pacified':
      verb = 'uniq.pac'
    elif match[0][0] == 'enslaved':
      verb = 'uniq.ens'
    elif match[0][0] == 'slimified':
      verb = 'uniq.sli'
    noun = strip_unique_qualifier(match[0][1])

  if verb == 'br.enter':
    noun = R_BRANCH_ENTER.findall(d['place'])[0]
  if verb == 'br.end':
    noun = R_BRANCH_END.findall(d['place'])[0]
  if verb == 'br.exit':
    noun = R_BRANCH_EXIT.findall(d['oplace'])[0]

  if verb == 'ghost':
    match = R_MILE_GHOST.findall(milestone)
    if match[0][0] == 'banished':
      verb = 'ghost.ban'
    elif match[0][0] == 'pacified':
      verb = 'ghost.pac'
    noun = match[0][1]
  if verb == 'rune':
    noun = R_RUNE.findall(milestone)[0]
  if verb == 'god.worship':
    noun = R_GOD_WORSHIP.findall(milestone)[0]
  elif verb == 'god.renounce':
    noun = R_GOD_RENOUNCE.findall(milestone)[0]
  elif verb == 'god.mollify':
    noun = R_GOD_MOLLIFY.findall(milestone)[0]
  elif verb == 'god.maxpiety':
    noun = R_GOD_MAXPIETY.findall(milestone)[0]
  if verb == 'orb':
    noun = 'orb'
  if verb == 'sacrifice':
    noun = R_SACRIFICE.findall(milestone)[0]
  noun = noun or milestone
  d['verb'] = verb
  d['type'] = verb
  d['noun'] = noun

def xlog_match(ref, target):
  """Returns True if all keys in the given reference dictionary are
associated with the same values in the target dictionary."""
  for key in ref.keys():
    if ref[key] != target.get(key):
      return False
  return True

def xlog_dict(logline):
  d = parse_logline(logline.strip())
  # Fake a raceabbr field.
  if d.get('char'):
    d['raceabbr'] = d['char'][0:2]

  if d.get('tmsg') and not d.get('vmsg'):
    d['vmsg'] = d['tmsg']

  if not d.get('tiles'):
    d['tiles'] = '0'

  if not d.get('nrune') and not d.get('urune'):
    d['nrune'] = 0
    d['urune'] = 0

  # Fixup rune madness where one or the other is set, but not both.
  if d.get('nrune') is not None or d.get('urune') is not None:
    d['nrune'] = d.get('nrune') or d.get('urune')
    d['urune'] = d.get('urune') or d.get('nrune')

  if record_is_milestone(d):
    xlog_milestone_fixup(d)
  xlog_set_killer_group(d)

  return d

def xlog_str(xlog):
  def xlog_escape(value):
    return isinstance(value, str) and value.replace(":", "::") or value
  return ":".join(["%s=%s" % (key, xlog_escape(xlog[key])) for key in xlog])

# The mappings in order so that we can generate our db queries with all the
# fields in order and generally debug things more easily.
LOG_DB_MAPPINGS = [
    [ 'v', 'version' ],
    [ 'lv', 'lv' ],
    [ 'name', 'player' ],
    [ 'uid', 'uid' ],
    [ 'race', 'race' ],
    [ 'raceabbr', 'raceabbr' ],
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
    [ 'int', 'intelligence' ],
    [ 'dex', 'dexterity' ],
    [ 'ac',  'ac' ],
    [ 'ev',  'ev' ],
    [ 'god', 'god' ],
    [ 'start', 'start_time' ],
    [ 'dur', 'duration' ],
    [ 'turn', 'turn' ],
    [ 'sc', 'score' ],
    [ 'ktyp', 'killertype' ],
    [ 'killer', 'killer' ],
    [ 'kgroup', 'kgroup' ],
    [ 'dam', 'damage' ],
    [ 'piety', 'piety' ],
    [ 'pen', 'penitence' ],
    [ 'end', 'end_time' ],
    [ 'tmsg', 'terse_msg' ],
    [ 'vmsg', 'verb_msg' ],
    [ 'kaux', 'kaux' ],
    [ 'kills', 'kills' ],
    [ 'nrune', 'nrune' ],
    [ 'urune', 'runes' ],
    [ 'gold', 'gold' ],
    [ 'goldfound', 'gold_found' ],
    [ 'goldspent', 'gold_spent' ]
    ]

MILE_DB_MAPPINGS = [
    [ 'v', 'version' ],
    [ 'lv', 'lv' ],
    [ 'name', 'player' ],
    [ 'uid', 'uid' ],
    [ 'race', 'race' ],
    [ 'raceabbr', 'raceabbr' ],
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
    [ 'int', 'intelligence' ],
    [ 'dex', 'dexterity' ],
    [ 'scrollsused', 'scrolls_used' ],
    [ 'potionsused', 'potions_used' ],
    [ 'god', 'god' ],
    [ 'start', 'start_time' ],
    [ 'dur', 'duration' ],
    [ 'turn', 'turn' ],
    [ 'dam', 'damage' ],
    [ 'piety', 'piety' ],
    [ 'nrune', 'nrune' ],
    [ 'urune', 'runes' ],
    [ 'verb', 'verb' ],
    [ 'noun', 'noun' ],
    [ 'milestone', 'milestone' ],
    [ 'time', 'milestone_time' ],
    ]

LOGLINE_TO_DBFIELD = dict(LOG_DB_MAPPINGS)
COMBINED_LOG_TO_DB = dict(LOG_DB_MAPPINGS + MILE_DB_MAPPINGS)

R_MONTH_FIX = re.compile(r'^(\d{4})(\d{2})(.*)')
R_GHOST_NAME = re.compile(r"^(.*)'s? ghost")
R_BRANCH_ENTER = re.compile(r"^(\w+)")
R_BRANCH_END = re.compile(r"^(\w+)")
R_BRANCH_EXIT = re.compile(r"^(\w+)")
R_MILESTONE_GHOST_NAME = re.compile(r"the ghost of ([^ ]*) the ")
R_KILL_UNIQUE = re.compile(r'^killed (.*)\.$')
R_MILE_UNIQ = re.compile(r'^(\w+) (.*)\.$')
R_MILE_GHOST = re.compile(r'^(\w+) the ghost of (\S+)')
R_RUNE = re.compile(r"found an? (.*) rune")
R_HYDRA = re.compile(r'^an? (\w+)-headed hydra')
R_PLACE_DEPTH = re.compile(r'^\w+:(\d+)')
R_GOD_WORSHIP = re.compile(r'^became a worshipper of (.*)\.$')
R_GOD_MOLLIFY = re.compile(r'^(?:partially )?mollified (.*)\.$')
R_GOD_RENOUNCE = re.compile(r'^abandoned (.*)\.$')
R_GOD_MAXPIETY = re.compile(r'^became the Champion of (.*)\.$')
R_SACRIFICE = re.compile(r'^sacrificed (?:an? )?(\w+)')

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
sqldatetime = SqlType(lambda x: fix_crawl_date(x[0:-1]))
bigint = SqlType(lambda x: int(x))
sql_int = bigint
varchar = char

dbfield_to_sqltype = {
	'player':char,
	'start_time':sqldatetime,
	'score':bigint,
	'race':char,
        'raceabbr':char,
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
	'intelligence':sql_int,
        'dexterity':sql_int,
        'ac':sql_int,
        'ev':sql_int,
        'scrolls_used':sql_int,
        'potions_used':sql_int,
	'god':char,
	'duration':sql_int,
	'turn':bigint,
	'runes':sql_int,
	'killertype':char,
	'killer':char,
        'kgroup' : char,
        'kaux':char,
	'damage':sql_int,
	'piety':sql_int,
        'penitence':sql_int,
	'end_time':sqldatetime,
        'milestone_time':sqldatetime,
	'terse_msg':varchar,
	'verb_msg':varchar,
        'nrune':sql_int,
        'kills': sql_int,
        'gold': sql_int,
        'gold_found': sql_int,
        'gold_spent': sql_int
	}

def record_is_milestone(rec):
  return rec.has_key('milestone') or rec.has_key('type')

def is_not_tourney(game):
  """A game started before the tourney start or played after the end
  doesn't count."""

  start = game.get('start')
  if not start:
    return True

  milestone = record_is_milestone(game)
  # Broken record checks:
  if not milestone and not game.get('end') and not game.get('time'):
    return True

  end = game.get('end') or game.get('time') or start

  # Is this the game version we want?
  if not game['v'].startswith(GAME_VERSION):
    return True

  return start < START_TIME or end >= END_TIME

def time_in_hare_window():
  nowtime = datetime.datetime.utcnow().strftime(DATE_FORMAT)
  return nowtime >= HARE_START_TIME

_active_cursor = None

def set_active_cursor(c):
  global _active_cursor
  _active_cursor = c

def active_cursor():
  global _active_cursor
  return _active_cursor

def query_do(cursor, query, *values):
  Query(query, *values).execute(cursor)

def query_first(cursor, query, *values):
  return Query(query, *values).first(cursor)

def query_first_def(cursor, default, query, *values):
  q = Query(query, *values)
  row = q.row(cursor)
  if row is None:
    return default
  return row[0]

def query_row(cursor, query, *values):
  return Query(query, *values).row(cursor)

def query_rows(cursor, query, *values):
  return Query(query, *values).rows(cursor)

def query_rows_with_ties(cursor, query, field, how_many, which_col, *values):
  first_query = query + (" ORDER BY %s DESC LIMIT %d" % (field, how_many))
  q = query_rows(cursor, first_query, *values)
  if len(q) < how_many:
    return q
  least_value = q[how_many-1][which_col]
  new_query = query + (" AND %s >= %d ORDER BY %s DESC" % (field, least_value, field))
  return query_rows(cursor, new_query, *values)

def query_first_col(cursor, query, *values):
  rows = query_rows(cursor, query, *values)
  return [x[0] for x in rows]

def _player_exists(c, name):
  """Return true if the player exists in the player table"""
  query = Query("""SELECT name FROM players WHERE name=%s;""",
                name)
  return query.row(c) is not None

player_exists = crawl_utils.Memoizer(_player_exists, lambda args: args[1 : ])

def add_player(c, name):
  """Add the given player with no score yet"""
  query_do(c,
           """INSERT INTO players (name, score_base, team_score_base)
              VALUES (%s, 0, 0);""",
           name)
  # And register with the Memoizer to let it know that the player now exists.
  player_exists.record((c, name), True)

def check_add_player(cursor, player):
  """Checks whether a player exists in the players table,
  adds an entry if not, suppressing exceptions."""
  try:
    if not player_exists(cursor, player):
      add_player(cursor, player)
  except MySQLdb.IntegrityError:
    # We don't care, this just means someone else added the player
    # just now. However we do need to update the player_exists cache.
    player_exists.record((cursor, player), True)

def update_player_fullscore(c, player, addition, team_addition):
  query_do(c,
           '''UPDATE players
              SET score_full = score_base + %s,
                  team_score_full = team_score_base + %s
              WHERE name = %s''',
           addition, team_addition, player)

def update_player_only_score(c, player, score):
  query_do(c,
           '''UPDATE players
              SET player_score_only = %s
              WHERE name = %s''',
           score, player)

def apply_dbtypes(game):
  """Given an xlogline dictionary, replaces all values with munged values
  that can be inserted directly into a db table. Keys that are not recognized
  (i.e. not in dbfield_to_sqltype) are ignored."""
  new_hash = { }
  for key, value in game.items():
    if (COMBINED_LOG_TO_DB.has_key(key) and
        dbfield_to_sqltype.has_key(COMBINED_LOG_TO_DB[key])):
      new_hash[key] = dbfield_to_sqltype[COMBINED_LOG_TO_DB[key]].to_sql(value)
    else:
      new_hash[key] = value
  return new_hash

def make_xlog_db_query(db_mappings, xdict, filename, offset, table):
  fields = ['source_file']
  values = [filename]
  if offset is not None and offset != False:
    fields.append('source_file_offset')
    values.append(offset)
  for logkey, sqlkey in db_mappings:
    if xdict.has_key(logkey):
      fields.append(sqlkey)
      values.append(xdict[logkey])
  return Query('INSERT INTO %s (%s) VALUES (%s);' %
               (table, ",".join(fields), ",".join([ "%s" for v in values])),
               *values)

def insert_xlog_db(cursor, xdict, filename, offset):
  milestone = record_is_milestone(xdict)
  db_mappings = milestone and MILE_DB_MAPPINGS or LOG_DB_MAPPINGS
  thingname = milestone and 'milestone' or 'logline'
  table = milestone and 'milestones' or 'games'
  save_offset = not milestone
  query = make_xlog_db_query(db_mappings, xdict, filename,
                             save_offset and offset, table)
  try:
    query.execute(cursor)
  except Exception, e:
    error("Error inserting %s %s (query: %s [%s]): %s"
          % (thingname, milestone, query.query, query.values, e))
    raise

def update_whereis(c, xdict, filename):
  player = xdict['name']
  src = filename[:3]
  # CDO tiles and console are separate. But CDO no longer has tiles.
  #if src == 'cdo' and xdict['tiles'] == '1':
  #  src = 'cdt'
  start_time = xdict['start']
  mile_time = xdict['time']
  query_do(c, '''INSERT INTO whereis_table
                      VALUES (%s, %s, %s, %s)
                 ON DUPLICATE KEY UPDATE start_time = %s, mile_time = %s''',
           player, src, start_time, mile_time, start_time, mile_time)

def update_last_game(c, xdict, filename):
  player = xdict['name']
  src = filename[:3]
  # CDO tiles and console are separate. But CDO no longer has tiles.
  #if src == 'cdo' and xdict['tiles'] == '1':
  #  src = 'cdt'
  start_time = xdict['start']
  query_do(c, '''INSERT INTO last_game_table
                      VALUES (%s, %s, %s)
                 ON DUPLICATE KEY UPDATE start_time = %s''',
           player, src, start_time, start_time)

def update_highscore_table(c, xdict, filename, offset, table, field, value):
  existing_score = query_first_def(c, 0,
                                   "SELECT score FROM " + table +
                                   " WHERE " + field + " = %s",
                                   value)
  if xdict['sc'] > existing_score:
    if existing_score > 0:
      query_do(c, "DELETE FROM " + table + " WHERE " + field + " = %s",
               value)
    iq = make_xlog_db_query(LOG_DB_MAPPINGS, xdict, filename, offset,
                            table)
    try:
      iq.execute(c)
    except Exception, e:
      error("Error inserting %s into %s (query: %s [%s]): %s"
            % (xdict, table, iq.query, iq.values, e))
      raise

def update_highscores(c, xdict, filename, offset):
  update_highscore_table(c, xdict, filename, offset,
                         table="combo_highscores",
                         field="charabbrev",
                         value=xdict['char'])
  update_highscore_table(c, xdict, filename, offset,
                         table="class_highscores",
                         field="class",
                         value=xdict['cls'])
  update_highscore_table(c, xdict, filename, offset,
                         table="species_highscores",
                         field="raceabbr",
                         value=xdict['char'][:2])

def dbfile_offset(cursor, table, filename):
  """Given a db cursor and filename, returns the offset of the last
  logline from that file that was entered in the db."""
  return query_first(cursor,
                     ('SELECT MAX(source_file_offset) FROM %s ' % table) + \
                       'WHERE source_file = %s',
                     filename)

def logfile_offset(cursor, filename):
  return (dbfile_offset(cursor, 'games', filename) or -1)

def milestone_offset(cursor, filename):
  return dbfile_offset(cursor, 'milestone_bookmark', filename) or -1

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

def extract_ghost_name(killer):
  return R_GHOST_NAME.findall(killer)[0]

def extract_milestone_ghost_name(milestone):
  return R_MILESTONE_GHOST_NAME.findall(milestone)[0]

def extract_rune(milestone):
  return R_RUNE.findall(milestone)[0]

def record_ghost_kill(cursor, game):
  """Given a game where the character was slain by a ghost, adds an entry in
  the kills_by_ghosts table."""
  query_do(cursor,
           '''INSERT INTO kills_by_ghosts
              (killed_player, killed_start_time, killer) VALUES
              (%s, %s, %s);''',
           game['name'], game['start'], extract_ghost_name(game['killer']))

def is_ghost_kill(game):
  killer = game.get('killer') or ''
  return R_GHOST_NAME.search(killer)

def process_log(cursor, filename, offset, d):
  if is_not_tourney(d):
    return

  # Add the player outside the transaction and suppress errors.
  check_add_player(cursor, d['name'])

  cursor.execute('BEGIN;')
  try:
    insert_xlog_db(cursor, d, filename, offset)
    update_last_game(cursor, d, filename)
    update_highscores(cursor, d, filename, offset)

    if is_ghost_kill(d):
      record_ghost_kill(cursor, d)

    # Tell the listeners to do their thang
    for listener in LISTENERS:
      listener.logfile_event(cursor, d)

    cursor.execute('COMMIT;')
  except:
    cursor.execute('ROLLBACK;')
    raise

def extract_unique_name(kill_message):
  return strip_unique_qualifier(R_KILL_UNIQUE.findall(kill_message)[0])

def _player_count_unique_uniques(cursor, player):
  """Given a player name, counts the number of distinct uniques the player
  has killed by trawling through the kills_of_uniques table. This is more
  expensive and lower-level than player_get_nunique_uniques, so use that
  where possible."""
  return query_first(cursor,
                     '''SELECT COUNT(DISTINCT monster)
                        FROM kills_of_uniques
                        WHERE player = %s''',
                     player)


def player_get_nunique_uniques(cursor, player):
  """Given a player name, looks up the number of distinct slain uniques
  for the player by checking the kunique_times ref table. This is less
  expensive than player_count_unique_uniques, and should be used unless
  you know that kunique_times is out-of-date."""
  return query_first_def(cursor,
                         0,
                         '''SELECT nuniques FROM kunique_times
                            WHERE player = %s''',
                         player)

def add_unique_milestone(cursor, game):
  if not game['milestone'].startswith('banished '):
    sqltime = game['time']
    query_do(cursor,
             '''INSERT INTO kills_of_uniques (player, kill_time, monster)
                VALUES (%s, %s, %s);''',
             game['name'],
             sqltime,
             extract_unique_name(game['milestone']))
    query_do(cursor,
             '''INSERT INTO kunique_turns (player, start_time, monster, turn)
                VALUES (%s, %s, %s, %s);''',
             game['name'],
             game['start'],
             extract_unique_name(game['milestone']),
             game['turn'])

    # Update a convenient lookup table that we can use for trophy calcs.
    uniqcount = _player_count_unique_uniques(cursor, game['name'])
    cachecount = player_get_nunique_uniques(cursor, game['name'])
    if uniqcount > cachecount:
      if cachecount == 0:
        query_do(cursor,
                 '''INSERT INTO kunique_times (player, nuniques, kill_time)
                    VALUES (%s, %s, %s)''',
                 game['name'], uniqcount, sqltime)
      else:
        query_do(cursor,
                 '''UPDATE kunique_times
                    SET nuniques = %s, kill_time = %s
                    WHERE player = %s
                    AND nuniques < %s''',
                 uniqcount, sqltime, game['name'], uniqcount)

def add_ghost_milestone(cursor, game):
  if not game['milestone'].startswith('banished '):
    query_do(cursor,
             '''INSERT INTO kills_of_ghosts (player, start_time, ghost)
                VALUES (%s, %s, %s);''',
             game['name'], game['time'],
             extract_milestone_ghost_name(game['milestone']))

def add_rune_milestone(cursor, game):
  query_do(cursor,
           '''INSERT INTO rune_finds (player, start_time, rune_time, rune, xl)
              VALUES (%s, %s, %s, %s, %s);''',
           game['name'], game['start'], game['time'],
           extract_rune(game['milestone']), game['xl'])

def add_br_enter_milestone(cursor, game):
  query_do(cursor,
           '''INSERT INTO branch_enters (player, start_time, mile_time, br)
              VALUES (%s, %s, %s, %s);''',
           game['name'], game['start'], game['time'],
           game['noun'])

def add_br_end_milestone(cursor, game):
  query_do(cursor,
           '''INSERT INTO branch_ends (player, start_time, mile_time, br)
              VALUES (%s, %s, %s, %s);''',
           game['name'], game['start'], game['time'],
           game['noun'])

def add_ziggurat_milestone(c, g):
  place = g['place']
  mtype = g['type']
  if mtype == 'zig.enter':
    level = 1
  else:
    level = int(R_PLACE_DEPTH.findall(place)[0])
  depth = level * 2
  # Leaving a ziggurat level by the exit gets more props than merely
  # entering the level.
  if mtype == 'zig.exit':
    depth += 1
  player = g['name']
  def player_ziggurat_deepest(player):
    return query_first_def(c, 0,
                           '''SELECT deepest FROM ziggurats
                              WHERE player = %s''',
                           player)
  deepest = player_ziggurat_deepest(g['name'])
  if depth > deepest:
    if deepest == 0:
      query_do(c,
               '''INSERT INTO ziggurats (player, deepest, place, zig_time,
                                         start_time)
                                VALUES (%s, %s, %s, %s, %s)''',
               player, depth, place, g['time'], g['start'])
    else:
      query_do(c,
               '''UPDATE ziggurats SET deepest = %s, place = %s,
                                       zig_time = %s, start_time = %s
                                 WHERE player = %s''',
               depth, place, g['time'], g['start'], player)

MILESTONE_HANDLERS = {
  'uniq' : add_unique_milestone,
  'ghost' : add_ghost_milestone,
  'rune' : add_rune_milestone,
  'br.enter': add_br_enter_milestone,
  'br.end': add_br_end_milestone,
  'zig.enter': add_ziggurat_milestone,
  'zig': add_ziggurat_milestone,
  'zig.exit': add_ziggurat_milestone,
}

def add_milestone_record(c, filename, offset, d):
  if is_not_tourney(d):
    return

  # Add player entry outside the milestone transaction.
  check_add_player(c, d['name'])

  # Start a transaction to ensure that we don't part-update tables.
  c.execute('BEGIN;')
  try:
    update_milestone_bookmark(c, filename, offset)
    insert_xlog_db(c, d, filename, offset)
    update_whereis(c, d, filename)
    handler = MILESTONE_HANDLERS.get(d['type'])
    if handler:
      handler(c, d)

    # Tell the listeners to do their thang
    for listener in LISTENERS:
      listener.milestone_event(c, d)

    c.execute('COMMIT;')
  except:
    c.execute('ROLLBACK;')
    raise

def add_listener(listener):
  LISTENERS.append(listener)

def add_timed(interval, timed):
  TIMERS.append(CrawlTimerState(interval, timed))

def define_timer(interval, fn):
  return (interval, CrawlTimerListener(fn))

def define_cleanup(fn):
  return CrawlCleanupListener(fn)

def run_timers(c, elapsed_time):
  for timer in TIMERS:
    timer.run(c, elapsed_time)

def load_extensions():
  c = ConfigParser.ConfigParser()
  c.read(EXTENSION_FILE)

  exts = c.get('extensions', 'ext') or ''

  for ext in exts.split(','):
    key = ext.strip()
    filename = key + '.py'
    info("Loading %s as %s" % (filename, key))
    module = imp.load_source(key, filename)
    if 'LISTENER' in dir(module):
      for l in module.LISTENER:
        add_listener(l)
    if 'TIMER' in dir(module):
      for t in module.TIMER:
        add_timed(*t)

def init_listeners(db):
  for e in LISTENERS:
    e.initialize(db)

def cleanup_listeners(db):
  for e in LISTENERS:
    e.cleanup(db)

def create_master_reader():
  blacklist = Blacklist(BLACKLIST_FILE)
  processors = ([ MilestoneFile(x) for x in MILESTONES ] +
                [ Logfile(x, blacklist) for x in LOGS ])
  return MasterXlogReader(processors)

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  crawl_utils.lock_or_die()
  print "Populating db (one-off) with logfiles and milestones. " + \
      "Running the taildb.py daemon is preferred."

  load_extensions()

  db = connect_db()
  init_listeners(db)

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

  cursor = db.cursor()
  support_mysql57(cursor)
  set_active_cursor(cursor)
  try:
    master = create_master_reader()
    master.tail_all(cursor)
  finally:
    set_active_cursor(None)
    cursor.close()

  cleanup_listeners(db)
  db.close()
