DELETE FROM combo_highscores WHERE player = '#NAME#';
DELETE FROM species_highscores WHERE player = '#NAME#';
DELETE FROM class_highscores WHERE player = '#NAME#';

DELETE FROM kills_of_ghosts WHERE player = '#NAME#';
DELETE FROM kills_of_uniques WHERE player = '#NAME#';
DELETE FROM rune_finds WHERE player = '#NAME#';
DELETE FROM branch_enters WHERE player = '#NAME#';
DELETE FROM branch_ends WHERE player = '#NAME#';
DELETE FROM ziggurats WHERE player = '#NAME#';
DELETE FROM whereis_table WHERE player = '#NAME#';
DELETE FROM last_game_table WHERE player = '#NAME#';
DELETE FROM player_won_gods WHERE player = '#NAME#';
DELETE FROM player_max_piety WHERE player = '#NAME#';
DELETE FROM player_maxed_skills WHERE player = '#NAME#';
DELETE FROM player_fifteen_skills WHERE player = '#NAME#';
DELETE FROM player_banners WHERE player = '#NAME#';
DELETE FROM clan_banners WHERE team_captain = '#NAME#';

UPDATE players SET team_captain = NULL WHERE team_captain = '#NAME#';

DELETE FROM games WHERE player = '#NAME#';
DELETE FROM milestones WHERE player = '#NAME#';
DELETE FROM players WHERE name = '#NAME#';
DELETE FROM teams WHERE owner = '#NAME#';


