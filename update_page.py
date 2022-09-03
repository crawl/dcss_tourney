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
import banner
from logging import debug, info, warn, error

import tourney_html as html ## XX fully rename
import scoring_data

CategoryResult = collections.namedtuple('CategoryResult', ('rank', 'best', 'details'))
BannerResult = collections.namedtuple('BannerResult', ('tier',))

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
    f.write(template_data.decode("utf-8"))
  finally:
    f.close()

def tourney_overview(c):
  info("Updating overview page")
  render(c, 'overview', top_level_pars=True)

def category_pages(c):
  for category_type, categories in (('individual', scoring_data.INDIVIDUAL_CATEGORIES), ('clan', scoring_data.CLAN_CATEGORIES)):
    prefix = "" if category_type == 'individual' else 'clan-'
    for category in categories:
      if not category.source_table:
        info("Not generating any page for %s category %s", category_type, category.name)
        continue
      info("Updating %s category page %s", category_type, category.name)
      rows = scoring_data.category_leaders(category, c)
      render(
        c,
        page='category',
        dest=prefix + crawl_utils.slugify(category.name),
        pars={
          'category': category,
          'rows': rows,
        },
        top_level_pars=True,
      )

def clan_category_pages(c):
  for category in scoring_data.CLAN_CATEGORIES:
    info("Updating clan category page %s" % category.name)
    render(
      c,
      page='category',
      dest='clan-' + crawl_utils.slugify(category.name),
      pars={
        'category': category,
      },
      top_level_pars=True,
    )

def player_pages(c):
  info("Updating all player pages")
#  render(c, 'banners')
  render(c, 'all-players-ranks')
#  render(c, 'wins-and-kills')
  render(c, 'current-games')
  render(c, 'combo-scoreboard')
  render(c, 'combo-leaders')
  render(c, 'killers')
  render(c, 'search')
  for p in query.get_players(c):
    player_page(c, p)

def index_page(c):
  info("Updating index page")
  render(c, 'index')
  #render(c, 'unique-list')

def team_page(c, captain):
  clan_info = query.get_clan_info(c, captain)
  assert clan_info is not None
  clan_name = clan_info[0]
  info("Updating team page for %s" % clan_name)

  stats = query.get_clan_stats(c, captain)

  pars = {
    'captain': captain,
    'clan_name': clan_name,
    'clan_members': clan_info[1],
    'overall_rank': stats['rank1'],
    'total_number_of_clans': stats['rank2'],
    'clan_category_results': clan_category_results(c, clan_name),
  }
  render(c, 'clan',
    dest = '%s/%s' % (
      crawl_utils.CLAN_BASE,
      crawl_utils.clan_page_name(clan_name, captain)),
    pars = pars, top_level_pars=True,
  )

def clan_category_results(c, clan_name):
  all_ranks = query.get_all_clan_ranks(c, pretty=False)
  clan_results = [result for result in all_ranks if result[0] == clan_name][0]
  data = {}
  for category, rank in zip(scoring_data.CLAN_CATEGORIES, clan_results[3:]):
    best = 0
    if category.proportional:
        best = category.max
    else:
        best = query.leader_score(c, category)
    data[category.name] = CategoryResult(rank, best, None)
  return data

def team_pages(c):
  info("Updating teams page")
  render(c, 'teams')
  for captain in query.get_team_captains(c):
    team_page(c, captain)

def player_page(c, player):
  info("Updating player page for %s" % player)
  stats = query.get_player_stats(c, player)
  player_params = {
    'player' : player,
    'score_full': stats['score_full'],
    'total_number_of_players': stats['rank2'],
    'overall_rank': stats['rank1'],
    'individual_category_results': player_individual_category_results(c, player),
    #'clan_category_results': player_clan_category_results(c, player),
    'banner_results': player_banner_results(c, player),
  }
  _clan_info = query.get_clan_info(c, player)
  if _clan_info is None:
    _clan_info = (None, [], None)
  player_params['clan_name'] = _clan_info[0]
  player_params['clan_members'] = _clan_info[1]
  player_params['clan_url'] = _clan_info[2]
  render(c, 'player',
         dest = ('%s/%s' % (crawl_utils.PLAYER_BASE, player.lower())),
         pars = player_params,
         top_level_pars=True)

def player_individual_category_results(c, player):
  data = {}
  ranks = query.get_player_ranks(c, player)
  for category in scoring_data.INDIVIDUAL_CATEGORIES:
    description = None
    best = 0
    if category.proportional:
        best = category.max
    else:
        best = query.leader_score(c, category)
    if ranks is None:
      data[category.name] = CategoryResult(None, best, description)
    else:
      data[category.name] = CategoryResult(ranks[category.name], best, description)

  return data

def player_clan_category_results(c, player):
  # TODO
  import random
  data = {}
  for category in scoring_data.CLAN_CATEGORIES:
    data[category.name] = CategoryResult(random.randrange(0, 10), 27, 'Details about clan challenge %s' % category.name)
  return data

def player_banner_results(c, player):
  data = {}
  for banentry in scoring_data.BANNERS:
    data[banentry.name] = BannerResult(banner.player_banner_tier(c, player,
        banentry.dbname))
  return data

# Update tourney overview every 5 mins.
INTERVAL = crawl_utils.UPDATE_INTERVAL
TIMER = [
          loaddb.define_timer( INTERVAL, tourney_overview ),
          loaddb.define_timer( INTERVAL, team_pages ),
          loaddb.define_timer( INTERVAL, player_pages ),
          loaddb.define_timer( INTERVAL, category_pages ),
          ]
LISTENER = [
             loaddb.define_cleanup(tourney_overview),
             loaddb.define_cleanup(team_pages),
             loaddb.define_cleanup(player_pages),
             loaddb.define_cleanup(category_pages),
           ]

if __name__ == '__main__':
  db = loaddb.connect_db()
  try:
    for l in LISTENER:
      l.cleanup(db)
  finally:
    db.close()
