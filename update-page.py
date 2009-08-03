#!/usr/bin/python

import mako.template
import mako.lookup
import os
import os.path
import loaddb
import query
import crawl_utils

from logging import debug, info, warn, error

TEMPLATE_DIR = os.path.abspath('templates')
MAKO_LOOKUP = mako.lookup.TemplateLookup(directories = [ TEMPLATE_DIR ])

def render(c, page, dest=None, pars=None):
  """Given a db context and a .mako template (without the .mako extension)
  renders the template and writes it back to <page>.html in the tourney
  scoring directory. Setting dest overrides the destination filename."""
  target = "%s/%s.html" % (crawl_utils.SCORE_FILE_DIR, dest or page)
  t = MAKO_LOOKUP.get_template(page + '.mako')
  try:
    f = open(target, 'w')

    pars = pars or { }
    pars['cursor'] = c

    try:
      f.write( t.render( attributes = pars ) )
    finally:
      f.close()
  except Exception, e:
    warn("Error generating page %s: %s" % (page, e))
    raise
    # Don't rethrow.

def tourney_overview(c):
  info("Updating overview page")
  render(c, 'overview')

def player_pages(c):
  info("Updating all player pages")
  for p in query.get_players(c):
    player_page(c, p)
  render(c, 'all-players')
  render(c, 'scoreboard')
  render(c, 'combo-scoreboard')
  render(c, 'combo-leaders')
  render(c, 'killers')
  render(c, 'gkills')

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
         pars = { 'player' : player })

# Update tourney overview every 5 mins.
INTERVAL = crawl_utils.UPDATE_INTERVAL
TIMER = [ loaddb.define_timer( INTERVAL, tourney_overview ),
          loaddb.define_timer( INTERVAL, team_pages ),
          loaddb.define_timer( INTERVAL, player_pages )
          ]
LISTENER = [ loaddb.define_cleanup(tourney_overview),
             loaddb.define_cleanup(team_pages),
             loaddb.define_cleanup(player_pages)
           ]

if __name__ == '__main__':
  db = loaddb.connect_db()
  try:
    for l in LISTENER:
      l.cleanup(db)
  finally:
    db.close()
