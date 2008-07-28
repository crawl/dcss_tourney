import MySQLdb

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


logline_to_dbfield = {'v':'version',
                      'lv':'lv',
                      'name':'player',
                      'uid':'uid',
                      'race':'race',
                      'cls':'class',
                      'char':'charabbrev',
                      'xl':'xl',
                      'sk':'skill',
                      'sklev':'sk_lev',
                      'title':'title',
                      'place':'place',
                      'br':'branch',
                      'lvl':'lvl',
                      'ltyp':'ltyp',
                      'hp':'hp',
                      'mhp':'maxhp',
                      'mmhp':'maxmaxhp',
                      'str':'strength',
                      'int':'intellegence',
                      'dex':'dexterity',
                      'god':'god',
                      'start':'start_time',
                      'dur':'duration',
                      'turn':'turn',
                      'sc':'score',
                      'ktyp':'killertype',
                      'killer':'killer',
                      'dam':'damage',
                      'piety':'piety',
                      'pen':'penitence',
                      'end':'end_time',
                      'tmsg':'terse_msg',
                      'vmsg':'verb_msg',
                      'kaux':'kaux',
                      'nrune':'nrune'}

class SqlType:
  def __init__(self, str_to_sql):
    print str_to_sql('1')
    self.str_to_sql = str_to_sql
  
  def to_sql(self, string):
    return (self.str_to_sql)(string)

char = SqlType(lambda x: '"' + MySQLdb.escape_string(x) + '"')
datetime = SqlType(lambda x: '"' + x[0:-1] + '"') #remove the trailing 'D'
bigint = SqlType(lambda x: str(int(x)))
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
        'nrune':sql_int
	}

def parenthesized_string(lst):
  ret = '('
  for elt in lst:
    ret += str(elt)
    ret += ', '
  #remove the trailing comma
  ret = ret[0:-2]
  ret +=')'
  return ret

def make_games_insert_query(logdict):
  fields = []
  values = []
  for key in logdict:
    field = logline_to_dbfield[key]
    type = dbfield_to_sqltype[field]
    fields.append(field)
    values.append(type.to_sql(logdict[key]))
  return """insert into games %s values %s;""" % (parenthesized_string(fields), parenthesized_string(values))



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

def read_file_into_games(db, filename):
  """Take a database with an open connection, and a name of a file, and 
  slurp the entire contents of the file into the games table of the database.
  This is pretty much only for testing."""
  f = open(filename)
  for line in f.readlines():
    d = parse_logline(line.strip())
    q = make_games_insert_query(d)
    db.query(q)