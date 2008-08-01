#!/usr/bin/python

import mako.template
import mako.lookup
import os
import os.path
import loaddb
import query

from logging import debug, info, warn, error

SCORE_FILE_DIR = '/var/www/crawl/tourney'
TEMPLATE_DIR = os.path.abspath('templates')

MAKO_LOOKUP = mako.lookup.TemplateLookup(directories = [ TEMPLATE_DIR ])

# So we have to update the scoring page pretty frequently.
# Right now I am just going to pseudocode the basic logic,
# because I am not actually fluent in Python.

def render(c, page):
  target = "%s/%s.html" % (SCORE_FILE_DIR, page)
  t = MAKO_LOOKUP.get_template(page + '.mako')
  try:
    f = open(target, 'w')
    try:
      f.write( t.render( attributes = { 'cursor' : c } ) )
    finally:
      f.close()
  except Exception, e:
    warn("Error generating page %s: %s" % (page, e))
    raise

def tourney_overview(c):
  info("Updating overview page")
  render(c, 'overview')

def update_scoring_page(c):
  """Master function!"""
  add_to_page(headers)
  add_to_page("<table border=1>")
  add_to_page("<tr>")
  new_table_element("Leading Players",
                    format_table("top_players", [ "Player", "Points" ],
                                 get_top_players(c)))
  new_table_element("Leading Clans", format_line(get_top_clans_in(c), clan, points))
  new_table_element("First Victory", format_line(get_first_victories_in(c), player, end_time))
  add_to_page("</tr>")
  add_to_page("<tr>")
  new_table_element("Fastest Realtime Win", format_line(get_fastest_realtime_wins_in(c), player, duration))
  new_table_element("Fastest Turncount Win", format_line(get_fastest_turncount_wins_in(c), player, duration))
  new_table_element("First All-Rune Win", format_line(get_first_allruners_in(c), player, end_time))
  add_to_page("</tr>")
  add_to_page("<tr>")
  new_table_element("Most Uniques Killed", format_line(most_uniques_killed_in(c), player, number))
  new_table_element("Most High Scores", format_line(most_high_scores_in(c), player, number))
  new_table_element("Lowest DL at XL 1", format_line(lowest_dl_in(c), player, dl))
  add_to_page("</tr>")
  add_to_page("<tr>")
  new_table_element("Most Uniques Killed: Clan", format_line(clan_most_uniques_killed_in(c), clan, number))
  new_table_element("Most High Scores: Clan", format_line(clan_most_high_scores_in(c), clan, number))
  new_table_element("Longest Streak", format_line(longest_streak_in(c), player, number))
  add_to_page("</tr>")
  add_to_page("</table><br><br>")
  add_to_page("Lowest High Scores:")
  add_to_page(format_line(lowest_high_scores_in(c), raceclass, score))
  add_to_page(footers)

def get_top_clans_in(c):
  """get the top three clans in the c"""

def get_first_victories_in(c):
  """get the first three victories in the c"""

def get_fastest_realtime_wins_in(c):
  """get the three fastest realtime wins in the c"""

def get_fastest_turncount_wins_in(c):
  """get the three fastest turncount wins in the c"""

def get_first_allruners_in(c):
  """get the first three all-rune victories in the c"""

def most_uniques_killed_in(c):
  """get the three players who have killed the most uniques"""

def most_high_scores_in(c):
  """get the three players with the most high scores"""

def lowest_dl_in(c):
  """get the three characters with the lowest xl1 dl"""

def clan_most_uniques_killed(c):
  """get the three clans with the most uniques killed"""

def clan_most_high_scores(c):
  """get the three clans with the most high scores"""

def longest_streak_in(c):
  """get the three players with the longest streaks"""

def lowest_high_scores_in(c):
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

# Update tourney overview every 5 mins.
TIMER = [ loaddb.define_timer( 5 * 60, tourney_overview ) ]

if __name__ == '__main__':
  c = query._cursor()
  tourney_overview(c)
