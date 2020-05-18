DELETE FROM combo_highscores WHERE player = '#NAME#';
DELETE FROM species_highscores WHERE player = '#NAME#';
DELETE FROM class_highscores WHERE player = '#NAME#';
DELETE FROM kills_by_ghosts WHERE killed_player = '#NAME#';
DELETE FROM kills_by_ghosts WHERE killer = '#NAME#';
DELETE FROM kills_of_ghosts WHERE player = '#NAME#';
DELETE FROM kills_of_uniques WHERE player = '#NAME#';
DELETE FROM kunique_times WHERE player = '#NAME#';
DELETE FROM rune_finds WHERE player = '#NAME#';
DELETE FROM branch_enters WHERE player = '#NAME#';
DELETE FROM branch_ends WHERE player = '#NAME#';
DELETE FROM ziggurats WHERE player = '#NAME#';
DELETE FROM whereis_table WHERE player = '#NAME#';
DELETE FROM last_game_table WHERE player = '#NAME#';
DELETE FROM player_won_gods WHERE player = '#NAME#';
DELETE FROM player_max_piety WHERE player = '#NAME#';
DELETE FROM player_points WHERE player = '#NAME#';
DELETE FROM player_stepdown_points WHERE player = '#NAME#';
DELETE FROM clan_stepdown_points WHERE captain = '#NAME#';
DELETE FROM clan_points WHERE captain = '#NAME#';
DELETE FROM deaths_to_uniques WHERE player = '#NAME#';
DELETE FROM deaths_to_distinct_uniques WHERE player = '#NAME#';
DELETE FROM player_maxed_skills WHERE player = '#NAME#';
DELETE FROM player_fifteen_skills WHERE player = '#NAME#';
DELETE FROM player_banners WHERE player = '#NAME#';
DELETE FROM clan_banners WHERE team_captain = '#NAME#';

UPDATE players SET team_captain = NULL WHERE team_captain = '#NAME#';

DELETE FROM games WHERE player = '#NAME#';
DELETE FROM milestones WHERE player = '#NAME#';
DELETE FROM players WHERE name = '#NAME#';
DELETE FROM teams WHERE owner = '#NAME#';


