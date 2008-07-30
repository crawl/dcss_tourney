#!/usr/bin/python

# So there are a few problems we have to solve:
# 1. Intercepting new logfile events
#    DONE: parsing a logfile line
#    TO DO: dealing with deaths 
# 2. Intercepting new milestone events (some of which we care about,
#    some of which we don't) 
# 3. Collecting data from whereis files
# 4. Determining who is the winner of various competitions based on the 
#    ruleset
# 5. Causing the website to be updated with who is currently winning everything
#    and, if necessary, where players are

# global variables
db = "/path/to/db" # since we only have the one, right?
starttime = # some long number

def parse_logline(logline):
  """This function takes a logfile line, which is mostly separated by colons,
  and parses it into a dictionary (which everyone except Python calls a hash).
  Because the Crawl developers are insane, a double-colon is an escaped colon,
  and so we have to be careful not to split the logfile on locations like
  D:7 and such. It also works on milestones and whereis."""
  # This is taken from Henzell. Yay Henzell!
  if not logline:
    # oops something is not right here  
  if logline[0] == ':' or (logline[-1] == ':' and not logline[-2] == ':'):
    # problem    
  if '\n' in logline:
    # problem 
  logline = replace(logline, "::", "\n")
  details = dict([(item[:item.index('=')], item[item.index('=') + 1:]) for item in logline.split(':')])
  for key in details:
    details[key] = replace(details[key], "\n", ":")
  return details 

def act_on_milestone(line):
  """This function takes a milestone line, which is a string composed of key/
  value pairs separated by colons, and parses it into a dictionary. 
  Then, depending on what type of milestone it is (key "type"), another 
  function may be called to finish the job on the milestone line. Milestones
  have the same broken :: behavior as logfile lines, yay."""
  this_mile = parse_logline(line)
  if is_too_early(this_mile['start']):
    return # games started before the tournament are worth diddly
  if this_mile['type'] == 'unique':
    do_milestone_unique(this_mile)
  if this_mile['type'] == 'rune':
    do_milestone_rune(this_mile)
  if this_mile['type'] == 'ghost':
    do_milestone_ghost(this_mile)
  return

def do_milestone_unique(mile):
  """This function takes a parsed milestone known to commemorate the death of
  a unique, and checks to see if the player has already killed the unique.
  If so, it does nothing; if not, it marks that the player has killed the 
  unique, and checks to see if the player has killed all uniques. If so, 
  the player may be awarded points if they are one of the first to do so."""
  unique = get_unique_name(this_mile['milestone'])
  if has_killed_unique(this_mile['name'], unique):
    return
  # write to db that this_mile['name'] killed unique
  # need help here
  assign_points(this_mile['name'], 5)
  if has_killed_all_uniques(this_mile['name']):
    # check to see if anyone else has done it yet, and assign points (50/20/10)
    # I think this requires doing a query and reacting to it?
  return

def get_unique_name(string):
  """The strings for killing uniques can vary, but the unique name always
  stays the same. This function takes the string and returns the name of the
  unique, since we don't care if Sigmund drowned or burned to a crisp or was
  banished or fell down the stairs or choked on his hat."""
  # list_of_uniques = some_sort_of_query
  for name in list_of_uniques: 
    if re.search(name, string):
      return name
    # otherwise it was a Pan lord or Geryon or someone we don't track

def has_killed_unique(player, unique):
  """Has the player killed this unique yet? Returns 1 or 0"""
  uniques_dead = #query db for uniques dead
  for name in uniques_dead:
    if name == unique:
      return 1
  return 0

def has_killed_all_uniques(player):
  """Has the player killed every unique in the game? Returns 1 or 0"""
  uniques_dead = #query db for uniques dead
  # oh god here comes a state machine! choo choooo!
  # basically for each unique, it confirms they are dead, and if it ever
  # fails to confirm, we stop looking. NOTE: put murray at the top to save
  # time, since he's impossible to find :)
  # list_of_uniques = query_again 
  for name in list_of_uniques:
    state = 0
    for dead in uniques_dead:
      if name == dead:
        state = 1
    if state = 0:
      return 0
  return 1

def do_milestone_rune(mile):
  """When the player gets a rune for the first time, they get ten points.
  After that, they get one point. This one is pretty simple."""
  if #player_already_has_rune:
    assign_points(db,mile['name'],1)
    return
  #log that player got rune
  assign_points(db,mile['name'], 10)
  return

def do_milestone_ghost(mile):
  """When you kill a player ghost, you get two clan points! Otherwise this
  isn't terribly remarkable."""
  assign_team_points(db,mile['name'],2)
  return

def act_on_logfile_line(line):
  """Actually assign things and write to the db based on a logfile line
  coming through. All lines get written to the db; some will assign 
  irrevocable points and those should be assigned immediately. Revocable
  points (high scores, lowest dungeon level, fastest wins) should be 
  calculated elsewhere."""
  this_game = parse_logline(line)
  if is_too_early(this_game['start']):
    return # this game does not count!
  make_games_insert_query(line)
  if this_game['ktyp'] == 'winning':
    crunch_winner(this_game) # lots of math to do for winners
  if re.search("\'s ghost",this_game['killer']):
    ghost = this.game['killer'].split("'")[0] #this line tested
    XL = this_game['xl']
    if XL>5:
      assign_points(db,ghost, (XL - 5)) 
  return

def crunch_winner(game):
  """A game that wins could assign a variety of irrevocable points for a 
  variety of different things. This function needs to calculate them all."""
  if is_all_runer(game): 
    all_allruners = number_of_allruners_before(game)
    if all_allruners=0:
      assign_points(db,game['name'],200)
    if all_allruners=1:
      assign_points(db,game['name'],100)
    if all_allruners=2:
      assign_points(db,game['name'],50)
    if it's my first all-rune win:
      assign_points(db,game['name'],50)
  all_wins = number_of_wins_before(game)
  if all_wins=0:
    assign_points(db,game['name'],200)
  if all_wins=1:
    assign_points(db,game['name'],100)
  if all_wins= 2:
    assign_points(db,game['name'],50)
  if it's my first all-rune win:
    assign_points(db,game['name'],50)
  my_wins = my_wins_before(game)
  if my_wins = 0: 
    assign_points(db,game['name'],100)
    return # I bet you don't have a streak
  if my_wins = 1:
    if count_wins(db, game['name'], game['race'], game['class'])=0:
      assign_points(db,game['name'],50)
  if is_on_streak(game):
    if count_wins(db, game['name'], game['race'], game['class'])>0:
      assign_points(db,game['name'],10) #lamer 
    else:
      if count_wins(db, game['name'], game['race'], None)>0:
        assign_points(db,game['name'],30) # repeat race
      else:
        if count_wins(db, game['name'], None, game['class'])>0:
	  assign_points(db,game['name'],30) # repeat class
	else:
	  assign_points(db,game['name'],100) # non-repeat!
  else:
    if count_wins(db, game['name'], game['race'], game['class'])>0:
      assign_points(db,game['name'],0) # You get NOTHING.
    else:
      if count_wins(db, game['name'], game['race'], None)>0:
        assign_points(db,game['name'],10) # repeat race
      else:
        if count_wins(db, game['name'], None, game['class'])>0:
          assign_points(db,game['name'],10) # repeat class
        else:
          assign_points(db,game['name'],30) # non-repeat!
  assign_points(db,game['name'],10) #every win gets at least 10 points no matter what

def is_on_streak(game):
  """Was the most recently ended game before this one a win?"""
  if some db munging:
    return 1
  return 0

def is_all_runer(game):
  """Did this game get every rune? This _might_ require checking the milestones
  associated with the start time..."""
  if some db munging:
    return 1
  return 0

def number_of_allruners_before(game):
  """How many all-runers happened before this game? We can stop at 3."""
  total=0
  for test_game in (games won before game):
    if is_all_runer(test_game):
      total = total + 1
      if total > 2:
        return 3
  return total

def number_of_wins_before(game):
  """How many wins happened before this game? We can stop at 3."""
  total=0
  for test_game in (games before game):
    if test_game['ktyp']='winning': 
      total = total + 1
      if total > 2:
        return 3
  return total

def my_wins_before(game):
  """How many wins did I have before this game? We can stop at 2."""
  total=0
  for test_game in (my games before game):
    if test_game['ktyp']='winning':
      total=total + 1
      if total > 1:
        return 2
  return total

def is_too_early(time):
  """A game started before the appropriate time doesn't count."""
  if time < start_time
    return 1 # yes, it's too early 
  return 0 # no, this game counts 

def whereis(player):
  """We might want to know where a player is, either to display it on the
  website or to... well, I can't think of another reason. This function 
  will give us a string to put on the site at the top of a player page
  or something similar."""
  # This is basically all pulled out of Henzell. Thanks, Henzell!
  # It's much messier than what I've done so far, but I want to 
  # avoid duplicating known-done work.
  rawdatapath = "/home/crawl/chroot/dgldir/ttyrec/"
  try:
    whereline = open(rawdatapath + '%s/%s.where' % (player, player)).readlines()[0][:-1]
  except IOError:
    return ("No whereis info for %s." % player) 
  details = parse_logline(whereline)
  version = details['v']
  if ':' in details['place']:
    prep = 'on'
  else:
    prep = 'in'
  prestr = godstr = datestr = turnstr_suffix = turnstr = ''
  try:
    godstr = ', a worshipper of %s,' % details['god']
  except KeyError:
    godstr = ''
  try:
    month = str(int(details['time'][4:6]) + 1)
    if len(month) < 2:
      month = '0' + month
    datestr = ' on %s-%s-%s' % (details['time'][0:4], month,
                                details['time'][6:8])
  except KeyError:
    datestr = ''
  nturns = int(details['turn'])
  status = details['status']
  if int(details['turn']) != 1:
    turnstr_suffix = 's'
  turnstr = ' after %d turn%s' % (int(details['turn']), turnstr_suffix)
  if status == 'saved':
    prestr = 'last saved'
  elif status in [ 'dead', 'quit', 'won', 'bailed out' ]:
    return ("%s is currently dead." % (player)) 
    # This should be changed to say where they died, but the Henzell
    # way to do that calls a ruby script so I am going to write my own.
  elif status == 'active':
    prestr = 'is currently'
    datestr = ''
  sktitle = game_skill_title(details)
  if (status != 'won') and (status != 'bailed out'):
    return ("%s the %s (L%s %s)%s %s %s %s%s%s." % (player, sktitle, details['xl'], details['char'], godstr, prestr, prep, replace(details['place'], ';', ':'), datestr, turnstr))
  return ("Whereis information for %s is not currently available." % (player))

