import os
import os.path
import logging
import fcntl
import sys

LOCK = None
BASEDIR = '/home/crawl'
LOCKFILE = BASEDIR + '/tourney-py.lock'
SCORE_FILE_DIR = '/var/www/crawl/tourney'
PLAYER_BASE = 'players'
CLAN_BASE = 'clans'
PLAYER_FILE_DIR = SCORE_FILE_DIR + '/' + PLAYER_BASE
CLAN_FILE_DIR = SCORE_FILE_DIR + '/' + CLAN_BASE

CAO_MORGUE_BASE = 'http://crawl.akrasiac.org/rawdata'
CDO_MORGUE_BASE = 'http://crawl.develz.org/morgues/stable'
CAO_BASE = 'http://crawl.akrasiac.org'
CAO_TOURNEY_BASE = '%s/tourney' % CAO_BASE
CAO_PLAYER_BASE = '%s/players' % CAO_TOURNEY_BASE
CAO_CLAN_BASE = '%s/clans' % CAO_TOURNEY_BASE

CAO_OVERVIEW = '''<a href="%s/overview.html">Overview</a>''' % CAO_TOURNEY_BASE

MKDIRS = [ SCORE_FILE_DIR, PLAYER_FILE_DIR, CLAN_FILE_DIR ]

for d in MKDIRS:
  if not os.path.exists(d):
    os.makedirs(d)

def lock_handle(check_only=True):
  if check_only:
    fcntl.flock(LOCK, fcntl.LOCK_EX | fcntl.LOCK_NB)
  else:
    fcntl.flock(LOCK, fcntl.LOCK_EX)

def lock_or_die(lockfile = LOCKFILE):
  global LOCK
  LOCK = open(lockfile, 'w')
  try:
    lock_handle()
  except IOError:
    sys.stderr.write("%s is locked, perhaps there's someone else running?\n" %
                     lockfile)
    sys.exit(1)

def daemonize(lockfile = LOCKFILE):
  global LOCK
  # Lock, then fork.
  LOCK = open(lockfile, 'w')
  try:
    lock_handle()
  except IOError:
    sys.stderr.write(("Unable to lock %s - check if another " +
                      "process is running.\n")
                     % lockfile)
    sys.exit(1)

  print "Starting daemon..."
  pid = os.fork()
  if pid is None:
    raise "Unable to fork."
  if pid == 0:
    # Child
    os.setsid()
    lock_handle(False)
  else:
    sys.exit(0)

class Memoizer:
  FLUSH_THRESHOLD = 1000

  """Given a function, caches the results of the function for sets of arguments
  and returns the cached result where possible. Do not use if you have
  very large possible combinations of args, or we'll run out of RAM."""
  def __init__(self, fn, extractor=None):
    self.fn = fn
    self.cache = { }
    self.extractor = extractor or (lambda baz: baz)

  def __call__(self, *args):
    if len(self.cache) > Memoizer.FLUSH_THRESHOLD:
      self.flush()
    key = self.extractor(args)
    if not self.cache.has_key(key):
      self.cache[key] = self.fn(*args)
    return self.cache[key]

  def flush(self):
    self.cache.clear()

  def record(self, args, value):
    self.cache[self.extractor(args)] = value


def format_time(time):
  return "%04d%02d%02d-%02d%02d%02d" % (time.year, time.month, time.day,
                                       time.hour, time.minute, time.second)

def player_link(player):
  return "%s/%s.html" % (CAO_PLAYER_BASE, player)

def clan_link(clan):
  return "%s/%s.html" % (CAO_CLAN_BASE, clan)

def morgue_link(xdict):
  """Returns a hyperlink to the morgue file for a dictionary that contains
  all fields in the games table."""
  src = xdict['source_file']
  name = xdict['player']

  stime = format_time( xdict['end_time'] )
  base = src.find('cao') >= 0 and CAO_MORGUE_BASE or CDO_MORGUE_BASE
  return "%s/%s/morgue-%s-%s.txt" % (base, name, name, stime)

def linked_text(key, link_fn, text=None):
  link = link_fn(key)
  return '<a href="%s">%s</a>' % (link, text or key)
