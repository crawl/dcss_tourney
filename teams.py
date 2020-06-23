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

BAD_NAMERS = ["penus"] # players who have lost the privilege of getting to name
                # their team in a given tourney

import os
import fnmatch
import re
import datetime

import loaddb
import query
import crawl_utils
import banner
import outline

import logging
from loaddb import query_first_col, player_blocklist
from logging import debug, info, warn, error

# Register listener and timer.

class TeamListener (loaddb.CrawlEventListener):
    def cleanup(self, db):
        cursor = db.cursor()
        loaddb.support_mysql57(cursor)
        try:
            insert_teams(cursor, get_teams(loaddb.CRAWLRC_DIRECTORY_LIST))
            update_clan_scores(cursor)
            db.commit()
        finally:
            cursor.close()

class TeamTimer (loaddb.CrawlTimerListener):
    def run(self, cursor, elapsed):
        insert_teams(cursor, get_teams(loaddb.CRAWLRC_DIRECTORY_LIST))
        update_clan_scores(cursor)

LISTENER = [ TeamListener() ]

# Run the timer every so often to refresh team stats.
TIMER = [ ( crawl_utils.UPDATE_INTERVAL , TeamTimer() ) ]

DEADLINE = loaddb.CLAN_DEADLINE

def get_teams(directory_list):
    '''Searches all *.rc files in the given directories for team information
    and returns a dictorary, indexed by team captains, of tuples of
    the team name and the set of members. If there are multiple .rc files belonging to the same player with team information, use the first one.'''
    existing_directory_list = [directory for directory in directory_list if os.path.exists(directory)]
    if len(existing_directory_list) == 0:
      return { }
    teams = {}
    teamname = {}
    draftees = {}
    volunteers = {}
    players = []
    for directory in existing_directory_list:
      for filename in os.listdir(directory):
        if fnmatch.fnmatch(filename, '*.sh'):
          shfile = open(os.path.join(directory, filename))
          linelist = [x.strip() for x in shfile.readlines()]
          shfile.close()
          count = 0
          max_count = len(linelist)
          while (count < max_count):
            line = linelist[count]
            player = line.split('.')[0].lower()
            if player in player_blocklist or player in players:
                count += 1
                continue
            linenum = line.split(':')[1]
            if linenum != "1":
                count += 1
                continue
            line = ':'.join(line.split(':')[2:])
            line = line[:111] # only 100 characters for team name
            offset = line.find('TEAM')
            if offset != -1:
                elements = re.sub('[^\w -]', '', line[offset:]).split(' ')
                if elements[0] == 'TEAMCAPTAIN':
                    players.append(player)
                    if len(elements) < 2:
                        elements.append(player)
                    volunteers.setdefault(elements[1].lower(), []).append(player)
                elif elements[0] == 'TEAMNAME':
                    players.append(player)
                    teamname[player] = ' '.join(elements[1:]) or ('Team_' + player)
                    if player in BAD_NAMERS:
                        teamname[player] = 'Team_' + player
                    volunteers.setdefault(player, []).append(player)
                    draftees[player] = [player]
                    if count + 1 == max_count:
                        break
                    line = linelist[count + 1]
                    draftees[player] = [player]
                    if line.split('.')[0].lower() == player and line.split(':')[1] == "2":
                        line = ':'.join(line.split(':')[2:])
                        offset = line.find('TEAM')
                        elements = re.sub('[^\w -]', '', line[offset:]).split(' ')
                        if elements[0] == 'TEAMMEMBERS':
                            draftedones = [name.lower() for name in elements[1:7]
                                           if name.lower() not in player_blocklist]
                            if player in draftedones:
                                draftees[player] = draftedones
                            else:
                                draftees[player] = draftedones[:5]
                                draftees[player].append(player)
            count += 1

        if fnmatch.fnmatch(filename, '*.rc'):
            player = filename[:-3].lower()
            if player in player_blocklist or player in players:
                continue
            rcfile = open(os.path.join(directory, filename))
            line = rcfile.readline()
            line = line[:111] # only 100 characters for team name
            offset = line.find('TEAM')
            if offset != -1:
                elements = re.sub('[^\w -]', '', line[offset:]).split(' ')
                if elements[0] == 'TEAMCAPTAIN':
                    players.append(player)
                    if len(elements) < 2:
                        elements.append(player)
                    volunteers.setdefault(elements[1].lower(), []).append(player)
                elif elements[0] == 'TEAMNAME':
                    players.append(player)
                    teamname[player] = ' '.join(elements[1:]) or ('Team_' + player)
                    if player in BAD_NAMERS:
                        teamname[player] = 'Team_' + player
                    volunteers.setdefault(player, []).append(player)
                    line = rcfile.readline()
                    offset = line.find('TEAM')
                    elements = re.sub('[^\w -]', '', line[offset:]).split(' ')
                    if elements[0] == 'TEAMMEMBERS':
                        draftedones = [name.lower() for name in elements[1:7]
                                       if name.lower() not in player_blocklist]
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

def update_clan_scores(c):
  banner.flush_clan_banners(c)
  query.update_all_clan_ranks(c)
  query.update_clan_scores(c)
  banner.assign_top_clan_banners(c)

  top_clan_player_banners = query.clan_player_banners(c)
  for banner_name, prestige, player in top_clan_player_banners:
    banner.award_banner(c, player, banner_name, prestige, temp=True)
