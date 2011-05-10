#This script assumes the following format:
#A team member should have the following as the first line of her rcfile:
# TEAMCAPTAIN <captain's name>
#The space serves as separator.
#The team captain should have the following as the first line of her rcfile:
# TEAMNAME <team name>
#The space serves as separator, spaces in the team name will be removed.
#Further, the team captain should have the following as the second line of her
#rcfile:
# TEAMMEMBERS <member1> <member2> ...
#A player is considered part of a team, if both she "volunteered" to the team's
#captain by putting the captain's name in her rcfile AND the captain "drafted"
#her by listing her as a member of the team, that she's also named.


import os
import fnmatch
import re
import datetime

import loaddb
import query
import crawl_utils
from query import say_points, get_points, log_temp_clan_points
import banner
import outline

import logging
from loaddb import query_first_col
from logging import debug, info, warn, error

# Register listener and timer.

class TeamListener (loaddb.CrawlEventListener):
    def cleanup(self, db):
        cursor = db.cursor()
        try:
            insert_teams(cursor, get_teams(loaddb.CRAWLRC_DIRECTORY))
            update_clan_scores(cursor)
        finally:
            cursor.close()

class TeamTimer (loaddb.CrawlTimerListener):
    def run(self, cursor, elapsed):
        insert_teams(cursor, get_teams(loaddb.CRAWLRC_DIRECTORY))
        update_clan_scores(cursor)

LISTENER = [ TeamListener() ]

# Run the timer every so often to refresh team stats.
TIMER = [ ( crawl_utils.UPDATE_INTERVAL , TeamTimer() ) ]

DEADLINE = datetime.datetime(2011, 5, 22, 0) # May 22, 00:00

def get_teams(directory):
    '''Searches all *.rc files in the given directory for team information
    and returns a dictorary, indexed by team capatains, of tuples of
    the team name and the set of members.'''
    if not os.path.exists(directory):
        return { }
    teams = {}
    teamname = {}
    draftees = {}
    volunteers = {}
    players = []
    for filename in os.listdir(directory):
        if fnmatch.fnmatch(filename, '*.rc'):
            player = filename[:-3].lower()
            players.append(player)
            rcfile = open(os.path.join(directory, filename))
            line = rcfile.readline()
            offset = line.find('TEAM')
            if offset != -1:
                elements = re.sub('[^\w -]', '', line[offset:]).split(' ')
                if elements[0] == 'TEAMCAPTAIN':
                    if len(elements) < 2:
                        elements.append(player)
                    volunteers.setdefault(elements[1].lower(), []).append(player)
                    line = rcfile.readline()
                    offset = line.find('TEAM')
                    elements = re.sub('[^\w -]', '', line[offset:]).split(' ')
                if elements[0] == 'TEAMNAME':
                    teamname[player] = ''.join(elements[1:]) or ('Team_' + player)
                    volunteers.setdefault(player, []).append(player)
                    line = rcfile.readline()
                    offset = line.find('TEAM')
                    elements = re.sub('[^\w -]', '', line[offset:]).split(' ')
                    if elements[0] == 'TEAMMEMBERS':
                        draftedones = [name.lower() for name in elements[1:7]]
                        if player in draftedones:
                            draftees[player] = draftedones
                        else:
                            draftees[player] = draftedones[:5]
                            draftees[player].append(player)
                    else:
                        draftees[player] = [player]
            rcfile.close()
    for captain in teamname.iterkeys():
        vset = set(volunteers.get(captain, []))
        dset = set(draftees.get(captain, []))
        members = vset.intersection(dset)
#        for name in members:
#            players.remove(name)
        teams[captain] = (teamname[captain], members)
#    for name in players:
#        teams[name] = ('Team_' + name, set([name]))
    return teams

def insert_teams(cursor, teams):
    now = datetime.datetime.utcnow()
    if (now < DEADLINE):
        info("Updating team information.")
        query.drop_teams(cursor)
        for captain in teams.iterkeys():
            loaddb.check_add_player(cursor, captain)
            canon_cap = query.canonicalize_player_name(cursor, captain)
            if canon_cap:
                query.create_team(cursor, teams[captain][0], canon_cap)
                for player in teams[captain][1]:
                    query.add_player_to_team(cursor, canon_cap, player)
    else:
        info("Team information frozen.")

# Team scoring. Putting it here because this we know the teams have
# been created in the db at this point.

def clan_additional_score(c, owner):
  additional = 0
  query.audit_flush_clan(c, owner)

  combo_pos = query.clan_combo_pos(c, owner)
  additional += log_temp_clan_points( c, owner,
                                      'combo_scores_Nth:%d' % (combo_pos + 1),
                                      get_points(
                                              combo_pos,
                                              200, 100, 50 ) )

  uscore_pos = query.clan_unique_pos(c, owner)
  additional += log_temp_clan_points( c, owner,
                                      'unique_kills_Nth:%d' % (uscore_pos + 1),
                                      get_points(
                                              uscore_pos,
                                              100, 50, 20 ) )

# Now we give race/class/combo points to clans.
  win_count = query.get_win_count(c)
  for g in query.clan_combo_wins(c, owner):
    key = 'combo_win:' + g[0]
    num_won = query.clan_count_combo_wins(c, g[0])
    if num_won == 1:
      points = 25
    else:
      points = (50 + num_won - 1) / num_won
    additional += log_temp_clan_points(c, owner, key, points)
  for g in query.clan_race_wins(c, owner):
    key = 'race_win:' + g[0]
    num_won = query.clan_count_race_wins(c, g[0])
    points = (2*win_count + num_won - 1) / num_won
    additional += log_temp_clan_points(c, owner, key, points)
  for g in query.clan_class_wins(c, owner):
    player = g[0]
    key = 'class_win:' + g[0]
    num_won = query.count_class_wins(c, g[0])
    points = (win_count + num_won - 1) / num_won
    additional += log_temp_clan_points(c, owner, key, points)

  query.set_clan_points(c, owner, additional)

def update_clan_scores(c):
  banner.flush_clan_banners(c)
  for clan in query.get_clans(c):
      info("Updating full score for clan %s" % clan)
      clan_additional_score(c, clan)
  banner.assign_top_clan_banners(c)

  top_clan_player_banners = query.clan_player_banners(c)
  for banner_name, player in top_clan_player_banners:
      banner.safe_award_banner(c, player, banner_name, 10, temp=True)
