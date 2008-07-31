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
  new_table_element("Leading Players", format_line(get_top_players_in(db), player, points))
  new_table_element("Leading Clans", format_line(get_top_clans_in(db), clan, points))
  new_table_element("First Victory", format_line(get_first_victories_in(db), player, end_time))
  add_to_page("</tr>")
  add_to_page("<tr>")
  new_table_element("Fastest Realtime Win", format_line(get_fastest_realtime_wins_in(db), player, duration))
  new_table_element("Fastest Turncount Win", format_line(get_fastest_turncount_wins_in(db), player, duration))
  new_table_element("First All-Rune Win", format_line(get_first_allruners_in(db), player, end_time))
  add_to_page("</tr>")
  add_to_page("<tr>")
  new_table_element("Most Uniques Killed", format_line(most_uniques_killed_in(db), player, number))
  new_table_element("Most High Scores", format_line(most_high_scores_in(db), player, number))
  new_table_element("Lowest DL at XL 1", format_line(lowest_dl_in(db), player, dl))
  add_to_page("</tr>")
  add_to_page("<tr>")
  new_table_element("Most Uniques Killed: Clan", format_line(clan_most_uniques_killed_in(db), clan, number))
  new_table_element("Most High Scores: Clan", format_line(clan_most_high_scores_in(db), clan, number))
  new_table_element("Longest Streak", format_line(longest_streak_in(db), player, number))
  add_to_page("</tr>")
  add_to_page("</table><br><br>")
  add_to_page("Lowest High Scores:")
  add_to_page(format_line(lowest_high_scores_in(db), raceclass, score))
  add_to_page(footers)
  
def get_top_players_in(db):
  """get the top three players in the db by points"""

def get_top_clans_in(db):
  """get the top three clans in the db""" 

def get_first_victories_in(db):
  """get the first three victories in the db"""

def get_fastest_realtime_wins_in(db):
  """get the three fastest realtime wins in the db"""

def get_fastest_turncount_wins_in(db):
  """get the three fastest turncount wins in the db"""

def get_first_allruners_in(db):
  """get the first three all-rune victories in the db"""

def most_uniques_killed_in(db):
  """get the three players who have killed the most uniques"""

def most_high_scores_in(db):
  """get the three players with the most high scores"""

def lowest_dl_in(db):
  """get the three characters with the lowest xl1 dl"""

def clan_most_uniques_killed(db):
  """get the three clans with the most uniques killed"""

def clan_most_high_scores(db):
  """get the three clans with the most high scores"""

def longest_streak_in(db):
  """get the three players with the longest streaks"""

def lowest_high_scores_in(db):
  """get the ten or so lowest high scores of any race/class combo"""

def new_table_element(string, function):
  add_to_page("<td>" + string + "\n" + function + "</td>")

def format_line(data, thing, sortindex):
  """Make a line of the appropriate sort for the thing and sortindex.
  Currently assumes we get things in order... and that sortindex works...
  which is a totally bogus assumption"""
  my_line = "<ul>" 
  for record in data:
    my_line= "<li>" + my_line + thing + " : " + sortindex + "</li>"
  my_line = my_line + "</ul>"
  return my_line

def add_to_page(string):
  """put together a page! yeah"""
  page = page + string + "\n"
  return
