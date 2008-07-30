#!/usr/bin/python

# So we have to update the scoring page pretty frequently. 
# Right now I am just going to pseudocode the basic logic,
# because I am not actually fluent in Python.

# "print" should be "write to file with an implicit newline" I think
# maybe write a function for that, maybe python does it automagically
# I don't even know

def update_scoring_page(db):
  """Master function!"""
  open up the file to write to
  print headers
  print "<table border=1>"
  print "<tr>"
  print "<td>Leading Players"
  leading_players_line = get_top_players_in(db)
  print leading_players_line
  print "</td>"
  print "<td>Leading Clans"
  leading_clans_line = get_top_clans_in(db)
  print "</td>"
  print "<td>First Victory"
  first_victory_line = get_first_victories_in(db)
  print "</td>"
  print "</tr>"
  print "<tr>"
  ...



def get_top_players_in(db):
  """get the top three players in the db and make a line for them in
  the front page. right now we just return a sample because I don't know
  how to do this."""
  return "<ul><li>Player1 : score</li><li>Player2: score</li><li>Player3 : score</li></ul>"

def get_top_players_in(db):
  """get the top three clans in the db and make a line for them in
  the front page. right now we just return a sample because I don't know
  how to do this."""
  return "<ul><li>Clan1 : score</li><li>Clan2 : score</li><li>Clan3 : score</li></ul>"

def get_first_victories_in(db):
  """yeah"""
  return "<ul><li>Player1 : time</li><li>Player2 : time</li><li>Player3 : time</li></ul>"

...

    
