import os
import os.path
import logging
import fcntl
import sys

# Update every so often (seconds)
UPDATE_INTERVAL = 7 * 60

# Are we testing locally? If so, use file:/// urls. The urls will be have the
# script working directory and then the SCORE_FILE_DIR added.
#
# If we're not testing locally and hence want output suitable for a web server,
# use urls made from WEB_BASE below. Set LOCAL_TEST="true" in env to enable.
if "LOCAL_TEST" in os.environ and os.environ["LOCAL_TEST"] == "true":
    LOCAL_TEST = True
else:
    LOCAL_TEST = False

# Base URL of tournament pages, omitting any trailing slash. This is not used
# if LOCAL_TEST is true.
if "WEB_BASE" in os.environ:
    WEB_BASE = os.environ["WEB_BASE"]
else:
    WEB_BASE = 'https://crawl.develz.org/tournament/0.24'

LOCK = None

# Where data needed for tournament calculations are stored. If BASEDIR env
# variable is defined, use that as the base directory.  Otherwise, use $HOME if
# we are LOCAL_TEST and a default if not.
if "BASEDIR" in os.environ:
    BASEDIR = os.environ["BASEDIR"]
elif LOCAL_TEST:
    BASEDIR = os.environ['HOME']
else:
    BASEDIR = '/home/tourney/dcss_tourney'

LOCKFILE = BASEDIR + '/tourney-py.lock'

# Where to generate the tournament pages. Can be a directory relative to
# current working directory of the script or a full path. Will be created if it
# doesn't exist.
SCORE_FILE_DIR = 'html.tourney0.24'

SCORE_CSS = 'tourney-score.css'
SCORE_CSS_PATH = SCORE_FILE_DIR + "/" + SCORE_CSS
PLAYER_BASE = 'players'
CLAN_BASE = 'clans'
PLAYER_FILE_DIR = SCORE_FILE_DIR + '/' + PLAYER_BASE
CLAN_FILE_DIR = SCORE_FILE_DIR + '/' + CLAN_BASE
IMAGE_FILE_DIR = SCORE_FILE_DIR + '/images'

CAO_MORGUE_BASE = 'http://crawl.akrasiac.org/rawdata'
CDO_MORGUE_BASE = 'http://crawl.develz.org/morgues/0.24'
CUE_MORGUE_BASE = 'https://underhound.eu/crawl/morgue'
CKO_MORGUE_BASE = 'https://crawl.kelbi.org/crawl/morgue'
CBRO_MORGUE_BASE = 'http://crawl.berotato.org/crawl/morgue'
CPO_MORGUE_BASE = 'http://crawl.project357.org/morgue'
CWZ_MORGUE_BASE = 'https://webzook.net/soup/morgue/0.24'
CXC_MORGUE_BASE = 'http://crawl.xtahua.com/crawl/morgue'
LLD_MORGUE_BASE = 'http://lazy-life.ddo.jp:8080/morgue-0.24'

if LOCAL_TEST:
    XXX_TOURNEY_BASE = 'file:///' + os.getcwd() + '/' + SCORE_FILE_DIR
else:
    XXX_TOURNEY_BASE = WEB_BASE

XXX_IMAGE_BASE = XXX_TOURNEY_BASE + '/images'
XXX_PLAYER_BASE = '%s/players' % XXX_TOURNEY_BASE
XXX_CLAN_BASE = '%s/clans' % XXX_TOURNEY_BASE

TAILDB_STOP_REQUEST_FILE = os.path.join(BASEDIR, 'taildb.stop')

MKDIRS = [ SCORE_FILE_DIR, PLAYER_FILE_DIR, CLAN_FILE_DIR, IMAGE_FILE_DIR ]

LOGFORMAT = "%(asctime)s [%(levelname)s] %(message)s"

def setup_scoring_dirs():
  for d in MKDIRS:
    if not os.path.exists(d):
      os.makedirs(d)
  os.system("cp {cwd}/templates/style.css {dest}".format(
    cwd=os.getcwd(),
    dest=SCORE_FILE_DIR + "/style.css",
  ))
  os.system("cp {cwd}/templates/script.js {dest}".format(
    cwd=os.getcwd(),
    dest=SCORE_FILE_DIR + "/script.js",
  ))
  # Legacy CSS
  if not os.path.exists(SCORE_CSS_PATH):
    os.system("cp %s/templates/%s %s" % (os.getcwd(), SCORE_CSS,
                                            SCORE_CSS_PATH))

  os.system("cp -r %s/images/* %s" % (os.getcwd(), IMAGE_FILE_DIR))

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

  print("Starting daemon...")
  pid = os.fork()
  if pid is None:
    raise Exception("Unable to fork.")
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

def base_link(s):
  return XXX_TOURNEY_BASE + "/" + s

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
  elif src.find('cue') >= 0:
    base = CUE_MORGUE_BASE
  elif src.find('cbr') >= 0:
    base = CBRO_MORGUE_BASE
  elif src.find('cpo') >= 0:
    base = CPO_MORGUE_BASE
  elif src.find('cwz') >= 0:
    base = CWZ_MORGUE_BASE
  elif src.find('cxc') >= 0:
    base = CXC_MORGUE_BASE
  elif src.find('cko') >= 0:
    base = CKO_MORGUE_BASE
  elif src.find('lld') >= 0:
    base = LLD_MORGUE_BASE
  else:
    raise Exception("Unknown server: " + src)
  return "%s/%s/morgue-%s-%s.txt" % (base, name, name, stime)

def linked_text(key, link_fn, text=None):
  link = link_fn(key)
  return '<a href="%s">%s</a>' % (link, (text or key).replace('_', ' '))

def clan_affiliation(player, clan_info, include_clan=True):
  # Clan affiliation info is clan name, followed by a list of players,
  # captain first, or None if the player is not in a clan.
  clan_name, players, page_name = clan_info
  if include_clan:
    clan_html = linked_text(page_name, clan_link, clan_name) + " - "
  else:
    clan_html = ''

  plinks = [ linked_text(players[0], player_link) + " (captain)" ]

  other_players = sorted(players[1:])
  for p in other_players:
    plinks.append( linked_text(p, player_link) )

  clan_html += ", ".join(plinks)
  return clan_html
