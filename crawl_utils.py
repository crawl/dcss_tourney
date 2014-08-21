import os
import os.path
import logging
import fcntl
import sys

# Update every so often (seconds)
UPDATE_INTERVAL = 7 * 60

# Are we testing locally, or do we want output suitable for a website?
# Test whether our username is the same that is used on the server.
LOCAL_TEST = ('tourney' != os.environ.get('USER'))
WEB_BASE = 'http://dobrazupa.org/tournament/0.15'

LOCK = None
BASEDIR = LOCAL_TEST and os.environ['HOME'] or '/home/tourney/dcss_tourney'
LOCKFILE = BASEDIR + '/tourney-py.lock'
SCORE_FILE_DIR = 'html.tourney0.15'

SCORE_CSS = 'tourney-score.css'
SCORE_CSS_PATH = SCORE_FILE_DIR + "/" + SCORE_CSS
PLAYER_BASE = 'players'
CLAN_BASE = 'clans'
PLAYER_FILE_DIR = SCORE_FILE_DIR + '/' + PLAYER_BASE
CLAN_FILE_DIR = SCORE_FILE_DIR + '/' + CLAN_BASE

CAO_MORGUE_BASE = 'http://crawl.akrasiac.org/rawdata'
CDO_MORGUE_BASE = 'http://crawl.develz.org/morgues/0.15'
CLN_MORGUE_BASE = 'http://crawl.lantea.net/crawl/morgue'
CSZO_MORGUE_BASE = 'http://dobrazupa.org/morgue'
CBRO_MORGUE_BASE = 'http://crawl.berotato.org/crawl/morgue'
CKR_MORGUE_BASE = 'http://kr.dobrazupa.org/morgue/0.15'
RHF_MORGUE_BASE = 'http://rl.heh.fi/morgue'

XXX_TOURNEY_BASE = ((LOCAL_TEST and ('file:///' + os.getcwd() + '/' + SCORE_FILE_DIR))
                   or WEB_BASE)
XXX_IMAGE_BASE = XXX_TOURNEY_BASE + '/images'
XXX_PLAYER_BASE = '%s/players' % XXX_TOURNEY_BASE
XXX_CLAN_BASE = '%s/clans' % XXX_TOURNEY_BASE

TAILDB_STOP_REQUEST_FILE = os.path.join(BASEDIR, 'taildb.stop')

MKDIRS = [ SCORE_FILE_DIR, PLAYER_FILE_DIR, CLAN_FILE_DIR ]

def setup_scoring_dirs():
  for d in MKDIRS:
    if not os.path.exists(d):
      os.makedirs(d)
  if not os.path.exists(SCORE_CSS_PATH):
    os.system("ln -s %s/templates/%s %s" % (os.getcwd(), SCORE_CSS,
                                            SCORE_CSS_PATH))

  images_link = SCORE_FILE_DIR + "/images"
  if not os.path.exists(images_link):
    os.system("ln -s %s/images %s" % (os.getcwd(), images_link))

setup_scoring_dirs()

def write_taildb_stop_request():
  f = open(TAILDB_STOP_REQUEST_FILE, 'w')
  f.write("\n")
  f.close()

def clear_taildb_stop_request():
  if os.path.exists(TAILDB_STOP_REQUEST_FILE):
    os.unlink(TAILDB_STOP_REQUEST_FILE)

def taildb_stop_requested():
  return os.path.exists(TAILDB_STOP_REQUEST_FILE)

def unlock_handle():
  fcntl.flock(LOCK, fcntl.LOCK_UN)

def lock_handle(check_only=True):
  if check_only:
    fcntl.flock(LOCK, fcntl.LOCK_EX | fcntl.LOCK_NB)
  else:
    fcntl.flock(LOCK, fcntl.LOCK_EX)

def lock_or_throw(lockfile = LOCKFILE):
  global LOCK
  LOCK = open(lockfile, 'w')
  lock_handle()

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
  return "%s/%s.html" % (XXX_PLAYER_BASE, player.lower())

def linked_player_name(player):
  return linked_text(player, player_link)

def clan_link(clan):
  return "%s/%s.html" % (XXX_CLAN_BASE, clan.lower())

def banner_link(banner):
  return XXX_IMAGE_BASE + '/' + banner

def morgue_link(xdict):
  """Returns a hyperlink to the morgue file for a dictionary that contains
  all fields in the games table."""
  src = xdict['source_file']
  name = xdict['player']

  stime = format_time( xdict['end_time'] )
  if src.find('cao') >= 0:
    base = CAO_MORGUE_BASE
  elif src.find('cdo') >= 0:
    base = CDO_MORGUE_BASE
  elif src.find('cln') >= 0:
    base = CLN_MORGUE_BASE
  elif src.find('csz') >= 0:
    base = CSZO_MORGUE_BASE
  elif src.find('cbr') >= 0:
    base = CBRO_MORGUE_BASE
  else:
    base = CKR_MORGUE_BASE
  return "%s/%s/morgue-%s-%s.txt" % (base, name, name, stime)

def linked_text(key, link_fn, text=None):
  link = link_fn(key)
  return '<a href="%s">%s</a>' % (link, (text or key).replace('_', ' '))
