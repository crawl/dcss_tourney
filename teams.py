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

import loaddb
import query
from query import say_points, get_points

import logging
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

# Run the timer every 5 minutes to refresh team stats.
TIMER = [ ( 5 * 60 , TeamTimer() ) ]

def get_teams(directory):
    '''Searches all *.crawlrc files in the given directory for team information
    and returns a dictorary, indexed by team capatains, of tuples of
    the team name and the set of members.'''
    teams = {}
    teamname = {}
    draftees = {}
    volunteers = {}
    players = []
    for filename in os.listdir(directory):
        if fnmatch.fnmatch(filename, '*.crawlrc'):
            player = filename[:-8].lower()
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
    info("Updating team information.")
    for captain in teams.iterkeys():
        loaddb.check_add_player(cursor, captain)
        canon_cap = query.canonicalize_player_name(cursor, captain)
        if canon_cap:
            query.create_team(cursor, teams[captain][0], canon_cap)
            for player in teams[captain][1]:
                query.add_player_to_team(cursor, canon_cap, player)


# Team scoring. Putting it here because this we know the teams have
# been created in the db at this point.

def clan_additional_score(c, owner):
  additional = 0
  clan = "CLAN %s" % owner
  additional += say_points( clan, 'combo_scores',
                            get_points( query.clan_combo_pos(c, owner),
                                        200, 100, 50 ) )
  additional += say_points( clan, 'unique_scores',
                            get_points( query.clan_unique_pos(c, owner),
                                        100, 50, 20 ) )
  # Clan that gets all uniques first. :P
  query.set_clan_points(c, owner, additional)

def update_clan_scores(c):
  for clan in query.get_clans(c):
    info("Updating full score for clan %s" % clan)
    clan_additional_score(c, clan)
