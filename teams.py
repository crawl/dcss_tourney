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

import query

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
            player = filename[:-8]
            players.append(player)
            rcfile = open(filename)
            firstline = rcfile.readline()
            offset = firstline.find('TEAM')
            if offset != -1:
                elements = re.sub('[^\w -]', '', firstline[offset:]).split(' ')
                if elements[0] == 'TEAMCAPTAIN':
                    volunteers.setdefault(elements[1], []).append(player)
                elif elements[0] == 'TEAMNAME':
                    teamname[player] = ''.join(elements[1:])
                    volunteers.setdefault(player, []).append(player)
                    secondline = rcfile.readline()
                    offset = firstline.find('TEAM')
                    elements = secondline[offset:].rstrip().split(' ')
                    if elements[0] == 'TEAMMEMBERS':
                        draftees[player] = elements[1:6]
                        draftees[player].append(player)
                    else:
                        draftees[player] = [player]
            rcfile.close()
    for captain in teamname.iterkeys():
        vset = set(volunteers.get(captain, []))
        dset = set(draftees.get(captain, []))
        members = vset.intersection(dset)
        for name in members:
            players.remove(name)
        teams[captain] = (teamname[captain], members)
    for name in players:
        teams[name] = ('Team_' + name, set([name]))
    return teams

def insert_teams(cursor, teams):
    for captain in teams.iterkey():
    	query.create_team(cursor, teams[captain][0], captain)
	for player in teams[captain][1]:
	    query.add_player_to_team(cursor, captain, player)

