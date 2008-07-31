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
#That part isn't implemented yet, though.

import os
import fnmatch

def get_teams(directory):
    '''Searches all *.crawlrc files in the given directory for team
    information.'''
    teamname = {}
    draftees = {}
    volunteers = {}
    for filename in os.listdir(directory):
        if fnmatch.fnmatch(filename, '*.crawlrc'):
            player = filename[:-8]
            rcfile = open(filename)
            firstline = rcfile.readline()
            offset = firstline.find('TEAM')
            if offset == -1:
                teamname[player] = 'Team_' + player
                draftees[player] = [player]
                volunteers[player] = [player]
            else:
                elements = firstline[offset:].rstrip().split(' ')
                if elements[0] == 'TEAMCAPTAIN':
                    volunteers.setdefault(elements[1], []).append(player)
                elif elements[0] == 'TEAMNAME':
                    teamname[player] = ''.join(elements[1:])
                    volunteers.setdefault(elements[1], []).append(player)
                    secondline = rcfile.readline()
                    offset = firstline.find('TEAM')
                    elements = secondline[offset:].rstrip().split(' ')
                    if elements[0] == 'TEAMMEMBERS':
                        draftees[player] = elements[1:]
                    else:
                        draftees[player] = [player]
                        volunteers[player] = [player]

