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
                      'end':'end_time',
                      'tmsg':'terse_msg',
                      'vmsg':'verb_msg',
                      'kaux':'kaux'}

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
	'end_time':datetime, 
	'terse_msg':varchar, 
	'verb_msg':varchar
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