#!/usr/bin/python
# coding=utf8

import mako.template
import mako.lookup
import os
import os.path
import loaddb
import query
import crawl_utils
import collections
from logging import debug, info, warn, error

import scoring_data

CategoryResult = collections.namedtuple('CategoryResult', ('rank', 'details'))
BannerResult = collections.namedtuple('BannerResult', ('tier', 'details'))

TEMPLATE_DIR = os.path.abspath('templates')
MAKO_LOOKUP = mako.lookup.TemplateLookup(directories = [ TEMPLATE_DIR ],
  strict_undefined=True,
  # If we ever migrate to Py3, remove the following parameters
  # Ref: https://docs.makotemplates.org/en/latest/unicode.html
  input_encoding='utf-8', output_encoding='utf-8', default_filters=['decode.utf8'],
  )

def render(c, page, dest=None, pars=None, top_level_pars=False):
  """Given a db context and a .mako template (without the .mako extension)
  renders the template and writes it back to <page>.html in the tourney
  scoring directory. Setting dest overrides the destination filename.

  pars is a dictionary of parameters to pass through to renderer as 'attributes'.

  If top_level_pars is true, the items in pars are sent through as individual context items.
  """
  pars = pars or { }
  pars['cursor'] = c
  target = "%s/%s.html" % (crawl_utils.SCORE_FILE_DIR, dest or page)
  try:
    t = MAKO_LOOKUP.get_template(page + '.mako')
    if top_level_pars:
      assert 'attributes' not in pars
      template_data = t.render(attributes={}, **pars)
    else:
      template_data = t.render( attributes = pars )
  except:
    print("TEMPLATE ERROR")
    print(mako.exceptions.text_error_template().render())
    raise
  f = open(target, 'w')
  try:
    f.write(template_data)
  finally:
    f.close()

def tourney_overview(c):
  info("Updating overview page")
  render(c, 'overview')

def individual_category_pages(c):
  info("Updating individual category pages")
  render(c, 'first-win-order')
  render(c, 'first-allrune-win-order')
  render(c, 'win-percentage-order')
  render(c, 'high-score-order')
  render(c, 'low-tc-win-order')
  render(c, 'fastest-realtime-win-order')
  render(c, 'low-xl-win-order')
  render(c, 'piety-order')
  render(c, 'banner-order')
  render(c, 'exploration-order')
  render(c, 'harvest-order')
  render(c, 'zig-dive-order')
  render(c, 'nemelex-order')
  render(c, 'streak-order-active-streaks')

def player_pages(c):
  info("Updating all player pages")
  render(c, 'banners')
  render(c, 'all-players')
#  render(c, 'wins-and-kills')
  render(c, 'current-games')
  render(c, 'combo-scoreboard')
  render(c, 'combo-leaders')
  render(c, 'killers')
#  for p in query.get_players(c):
#    player_page(c, p)

def index_page(c):
  info("Updating index page")
  render(c, 'index')
  #render(c, 'unique-list')

def team_page(c, captain):
  info("Updating team page for captain %s" % captain)
  render(c, 'clan', dest = ('%s/%s' % (crawl_utils.CLAN_BASE, captain.lower())),
         pars = { 'captain' : captain })

def team_pages(c):
  info("Updating teams page")
  render(c, 'teams')
  for captain in query.get_team_captains(c):
    team_page(c, captain)

def player_page(c, player):
  info("Updating player page for %s" % player)
  player_params = {
    'player' : player,
    'total_number_of_players': 1325, # TODO
    'overall_rank': 70, # TODO
    'clan_name': 'Sif\'s Supergroup', # TODO
    'individual_category_results': player_individual_category_results(c, player),
    'clan_category_results': player_clan_category_results(c, player),
    'banner_results': player_banner_results(c, player),
  }
  render(c, 'player',
         dest = ('%s/%s' % (crawl_utils.PLAYER_BASE, player.lower())),
         pars = player_params,
         top_level_pars=True)

def player_individual_category_results(c, player):
  # TODO
  import random
  data = {}
  for category in scoring_data.INDIVIDUAL_CATEGORIES:
    data[category.name] = CategoryResult(random.randrange(0, 10), 'Details about individual challenge %s for %s' % (category.name, category.god))
  return data

def player_clan_category_results(c, player):
  # TODO
  import random
  data = {}
  for category in scoring_data.CLAN_CATEGORIES:
    data[category.name] = CategoryResult(random.randrange(0, 10), 'Details about clan challenge %s' % category.name)
  return data

def player_banner_results(c, player):
  # TODO
  import random
  data = {}
  for banner in scoring_data.BANNERS:
    data[banner.name] = BannerResult(random.randrange(0, 3), ("Tier 1 notes", "Tier 2 notes", "Tier 3 notes"))
  return data

# Update tourney overview every 5 mins.
INTERVAL = crawl_utils.UPDATE_INTERVAL
TIMER = [ #loaddb.define_timer( INTERVAL, tourney_overview ),
          #loaddb.define_timer( INTERVAL, team_pages ),
          loaddb.define_timer( INTERVAL, player_pages ),
          loaddb.define_timer( INTERVAL, individual_category_pages )
          ]
LISTENER = [ #loaddb.define_cleanup(tourney_overview),
             #loaddb.define_cleanup(team_pages),
             loaddb.define_cleanup(player_pages),
             loaddb.define_cleanup(individual_category_pages)
           ]

if __name__ == '__main__':
  db = loaddb.connect_db()
  try:
    for l in LISTENER:
      l.cleanup(db)
  finally:
    db.close()
