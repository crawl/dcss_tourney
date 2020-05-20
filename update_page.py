#!/usr/bin/python
# coding=utf8

import mako.template
import mako.lookup
import os
import os.path
import loaddb
import query
import crawl_utils

from logging import debug, info, warn, error

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
  render(c, 'player',
         dest = ('%s/%s' % (crawl_utils.PLAYER_BASE, player.lower())),
         pars = { 'player' : player,
          # START FAKE DATA
          'MAX_POINTS': 10000,
          'total_number_of_players': 1325,
          'overall_rank': 70,
          'categories': [
            {
              'name': 'The Shining One',
              'desc': 'The Shining One values perserverence and courage in the face of adversity. In this category, TSO will award players 10,000 points if they win two distinct character combos, 5,000 points for winning their first combo, and 0 otherwise.',
              'player_rank': 0,
              'rank_details': 'Won combos: <a href="http://example.com/morgue.txt">MiFi</a>'
            },
            {
              'name': 'Cheibriados',
              'desc': 'Cheibriados believes in being slow and steady, and will recognize players who are careful enough to excel consistently. This category ranks players by their adjusted win percentage, calculated as the number of wins divided by the number of games played plus 1.',
              'player_rank': 1,
              'rank_details': 'Adjusted win percentage: 32.14% (9 wins in 27 games)'
            },
            {
              'name': 'Jiyva',
              'desc': u'Jiyva is ranking players by their streak length. Jiyva favours the flexibility of a gelatinous body—the length of a streak is defined as the number of distinct species or backgrounds won consecutively (whichever is smaller). Every game in a streak must be the first game you start after winning the previous game in the streak. This will always be the case if you play all your games on one server.',
              'player_rank': 2,
              'rank_details': 'No wins yet.',
            },
            {
              'name': 'Nemelex Xobeh',
              'desc': u'''Nemelex Xobeh wants to see players struggle against randomness and will rank players who perservere with one of several combos randomly chosen and announced throughout the tournament. The first 8 players to win a given Nemelex' choice combo earn a point in this category and Nemelex will rank players by their score in this category.''',
              'player_rank': 10000,
              'rank_details': 'Won combos: <a href="http://example.com/morgue.txt">MiFi</a>, <a href="http://example.com/morgue.txt">FeWz</a>, <a href="http://example.com/morgue.txt">BaFE</a>, <a href="http://example.com/morgue.txt">NaEE</a>, <a href="http://example.com/morgue.txt">GnSu</a>, <a href="http://example.com/morgue.txt">DrWn</a>, <a href="http://example.com/morgue.txt">HaCj</a>, <a href="http://example.com/morgue.txt">KoAs</a>'
            }
          ],
         },
         # END FAKE DATA
         top_level_pars=True)

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
