#!/usr/bin/python

# So we have to update the scoring page pretty frequently. 
# Right now I am just going to pseudocode the basic logic,
# because I am not actually fluent in Python.

page = "" # aw yeah global variables all up in this I am going to hell
          # HELL i tell you
headers = "<html><head><title>Crawl Tournament Leaderboard 2008</title></head><body>\n"
footers = "</body></html>"

def update_scoring_page(db):
  """Master function!"""
  add_to_page(headers)
  add_to_page("<table border=1>")
  add_to_page("<tr>")
  add_to_page("<td>Leading Players")
  leading_players_line = format_line(get_top_players_in(db), player, points)
  add_to_page(leading_players_line)
  add_to_page("</td>")
  add_to_page("<td>Leading Clans")
  leading_clans_line = format_line(get_top_clans_in(db), clan, points)
  add_to_page(leading_clans_line)
  add_to_page("</td>")
  add_to_page("<td>First Victory")
  first_victory_line = format_line(get_first_victories_in(db), player, end_time)
  add_to_page("</td>")
  add_to_page("</tr>")
  add_to_page("<tr>")
  add_to_page("<td>Fastest Realtime Win")
  fastest_realtime_line = format_line(get_fastest_realtime_wins_in(db), player, duration)
  add_to_page(fastest_realtime_line)
  add_to_page("</td>")
  add_to_page("<td>Fastest Turncount Win")
  fastest_turncount_line = format_line(get_fastest_turncount_wins_in(db), player, duration)
  add_to_page(fastest_turncount_line)
  add_to_page("</td>")
  add_to_page("<td>First All-Runer")
  first_allruner_line = format_line(get_first_allruners_in(db), player, end_time)
  add_to_page(first_allruner_line)
  add_to_page("</td>")
  add_to_page("</tr>")
  add_to_page("<tr>")



def get_top_players_in(db):
  """get the top three players in the db by points"""

def get_top_clans_in(db):
  """get the top three clans in the db""" 

def get_first_victories_in(db):
  """yeah"""

...

def format_line(data, thing, sortindex):
  """Make a line of the appropriate sort for the thing and sortindex.
  Currently assumes we get things in order..."""
  my_line = "<ul>" 
  for record in data:
    my_line= "<li>" + my_line + thing + " : " + sortindex + "</li>"
  my_line = my_line + "</ul>"
  return my_line

def add_to_page(string):
  """put together a page! yeah"""
  page = page + string + "\n"
  return
