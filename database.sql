-- Use InnoDB for transaction support?
-- SET storage_engine=InnoDB;

DROP TABLE IF EXISTS player_points;
DROP TABLE IF EXISTS clan_points;
DROP TABLE IF EXISTS deaths_to_distinct_uniques;
DROP TABLE IF EXISTS deaths_to_uniques;
DROP TABLE IF EXISTS player_maxed_skills;
DROP TABLE IF EXISTS player_fifteen_skills;
DROP TABLE IF EXISTS clan_banners;
DROP TABLE IF EXISTS player_banners;
DROP TABLE IF EXISTS player_won_gods;
DROP TABLE IF EXISTS player_max_piety;
DROP TABLE IF EXISTS active_streaks;
DROP TABLE IF EXISTS whereis_table;
DROP TABLE IF EXISTS last_game_table;
DROP TABLE IF EXISTS streaks;
DROP TABLE IF EXISTS ziggurats;
DROP TABLE IF EXISTS rune_finds;
DROP TABLE IF EXISTS branch_enters;
DROP TABLE IF EXISTS branch_ends;
DROP TABLE IF EXISTS kunique_times;
DROP TABLE IF EXISTS kunique_turns;
DROP TABLE IF EXISTS kills_of_uniques;
DROP TABLE IF EXISTS kills_of_ghosts;
DROP TABLE IF EXISTS kills_by_ghosts;
DROP TABLE IF EXISTS milestone_bookmark;
DROP TABLE IF EXISTS milestones;
DROP VIEW IF EXISTS class_highscores;
DROP VIEW IF EXISTS species_highscores;
DROP VIEW IF EXISTS combo_highscores;
DROP TABLE IF EXISTS combo_highscores;
DROP TABLE IF EXISTS class_highscores;
DROP TABLE IF EXISTS species_highscores;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS players;

DROP VIEW IF EXISTS fastest_realtime;
DROP VIEW IF EXISTS fastest_realtime_allruner;
DROP VIEW IF EXISTS fastest_turncount;
DROP VIEW IF EXISTS combo_win_highscores;
DROP VIEW IF EXISTS class_highscores;
DROP VIEW IF EXISTS game_species_highscores;
DROP VIEW IF EXISTS game_class_highscores;
DROP VIEW IF EXISTS game_combo_highscores;
DROP VIEW IF EXISTS clan_combo_highscores;
DROP VIEW IF EXISTS clan_total_scores;
DROP VIEW IF EXISTS clan_unique_kills;
DROP VIEW IF EXISTS clan_dated_unique_kills;
DROP VIEW IF EXISTS game_combo_win_highscores;
DROP VIEW IF EXISTS combo_hs_scoreboard;
DROP VIEW IF EXISTS combo_hs_clan_scoreboard;
DROP VIEW IF EXISTS streak_scoreboard;
DROP VIEW IF EXISTS best_ziggurat_dives;
DROP VIEW IF EXISTS youngest_rune_finds;
DROP VIEW IF EXISTS most_deaths_to_uniques;
DROP VIEW IF EXISTS have_hellpan_kills;
DROP VIEW IF EXISTS all_hellpan_kills;
DROP VIEW IF EXISTS fivefives_nine;
DROP VIEW IF EXISTS fivefives_rune;
DROP VIEW IF EXISTS fivefives_win;
DROP VIEW IF EXISTS orbrun_tomb;
DROP VIEW IF EXISTS nearby_uniques;
DROP VIEW IF EXISTS most_pacific_wins;
DROP VIEW IF EXISTS last_started_win;

CREATE TABLE IF NOT EXISTS players (
  name VARCHAR(20) PRIMARY KEY,
  team_captain VARCHAR(20),
  score_base BIGINT,
  -- This is the computed score! We will overwrite it each time we
  -- recalculate it, and it may be null at any point.
  score_full BIGINT DEFAULT 0,
  team_score_base BIGINT,
  -- This is also computed and will be overwritten each time.
  team_score_full BIGINT DEFAULT 0,
  -- So is this.
  player_score_only BIGINT DEFAULT 0,
  
  FOREIGN KEY (team_captain) REFERENCES players (name)
  ON DELETE SET NULL
  );
  
CREATE INDEX pscore ON players (score_full);

CREATE TABLE teams (
  owner VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  -- Clan total score, will be recomputed at intervals.
  total_score BIGINT DEFAULT 0 NOT NULL,
  PRIMARY KEY (owner),
  FOREIGN KEY (owner) REFERENCES players (name)
  ON DELETE CASCADE
  );

-- For mappings of logfile fields to columns, see loaddb.py
CREATE TABLE games (
  id BIGINT AUTO_INCREMENT,
  
  -- Source logfile
  source_file VARCHAR(150),
  -- Offset in the source file.
  source_file_offset BIGINT,

  player VARCHAR(20),
  start_time DATETIME,
  score BIGINT,
  race VARCHAR(20),
  -- Two letter race abbreviation so we can group by it without pain.
  raceabbr CHAR(2) NOT NULL,
  class VARCHAR(20),
  version VARCHAR(10),
  lv VARCHAR(8),
  uid INT,
  charabbrev CHAR(4),
  xl INT,
  skill VARCHAR(16),
  sk_lev INT,
  title VARCHAR(255),
  place CHAR(16),
  branch CHAR(16),
  lvl INT,
  ltyp CHAR(16),
  hp INT,
  maxhp INT,
  maxmaxhp INT,
  strength INT,
  intelligence INT,
  dexterity INT,
  god VARCHAR(20),
  duration INT,
  turn BIGINT,
  runes INT DEFAULT 0,
  killertype VARCHAR(20),
  killer CHAR(50),
  kgroup CHAR(50),
  kaux VARCHAR(255),
  -- Kills may be null.
  kills INT,
  damage INT,
  piety INT,
  penitence INT,
  gold INT,
  gold_found INT,
  gold_spent INT,
  end_time DATETIME,
  terse_msg VARCHAR(255),
  verb_msg VARCHAR(255),
  nrune INT DEFAULT 0,

  mapname VARCHAR(80) DEFAULT '',
  mapdesc VARCHAR(80) DEFAULT '',

  CONSTRAINT PRIMARY KEY (id)
  );

CREATE INDEX games_source_offset ON games (source_file, source_file_offset);

CREATE INDEX games_start_time_ktyp ON games (start_time, killertype);

CREATE INDEX games_scores ON games (player, score);
CREATE INDEX games_kgrp ON games (kgroup);
CREATE INDEX games_charabbrev_score ON games (charabbrev, score);
CREATE INDEX games_ktyp ON games (killertype);
CREATE INDEX games_p_ktyp ON games (player, killertype);

-- Index to find games with fewest kills.
CREATE INDEX games_kills ON games (killertype, kills);

-- Index to help us find fastest wins (time) quick.
CREATE INDEX games_win_dur ON games (killertype, duration);

-- Index to help us find fastest wins (turncount) quick.
CREATE INDEX games_win_turn ON games (killertype, turn);

CREATE TABLE combo_highscores AS
SELECT * FROM games;
ALTER TABLE combo_highscores DROP COLUMN id;

CREATE INDEX ch_player ON combo_highscores (player, killertype, score);
CREATE INDEX ch_killer ON combo_highscores (killertype);

CREATE TABLE species_highscores AS
SELECT * FROM games;
ALTER TABLE species_highscores DROP COLUMN id;
CREATE INDEX sh_player ON species_highscores (player, killertype, score);
CREATE INDEX sh_killer ON species_highscores (killertype);

CREATE TABLE class_highscores AS
SELECT * FROM games;
ALTER TABLE class_highscores DROP COLUMN id;
CREATE INDEX clh_player ON class_highscores (player, killertype, score);
CREATE INDEX clh_killer ON class_highscores (killertype);

CREATE TABLE milestones (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  -- Source milestone file
  source_file VARCHAR(150),

  -- The actual game that this milestone is linked with.
  game_id BIGINT,

  version VARCHAR(10),
  lv VARCHAR(8),
  
  cv VARCHAR(10),
  player VARCHAR(20),
  race VARCHAR(20),
  raceabbr CHAR(2) NOT NULL,
  class VARCHAR(20),
  charabbrev CHAR(4),
  xl INT,
  skill VARCHAR(16),
  sk_lev INT,
  title VARCHAR(50),
  place VARCHAR(16),

  branch VARCHAR(16),
  lvl INT,
  ltyp VARCHAR(16),
  hp INT,
  maxhp INT,
  maxmaxhp INT,
  strength INT,
  intelligence INT,
  dexterity INT,
  god VARCHAR(50),
  duration BIGINT,
  turn BIGINT,
  runes INT,
  nrune INT,

  -- Game start time.
  start_time DATETIME,

  -- Milestone time.
  milestone_time DATETIME,

  -- Known milestones: abyss.enter, abyss.exit, rune, orb, ghost, uniq,
  -- uniq.ban, br.enter, br.end, br.exit.
  verb VARCHAR(20),
  noun VARCHAR(100),

  -- The actual milestone message.
  milestone VARCHAR(255),

  FOREIGN KEY (game_id) REFERENCES games (id)
  ON DELETE SET NULL
);

CREATE INDEX milestone_verb ON milestones (player, verb);
CREATE INDEX milestone_noun ON milestones (noun, verb, player, start_time);
-- To find milestones belonging to a particular game.
CREATE INDEX milestone_lookup_by_time ON milestones (player, start_time, verb);

-- A table to keep track of the last milestone we've processed. This
-- will have only one row for one filename.
CREATE TABLE milestone_bookmark (
  source_file VARCHAR(150) PRIMARY KEY,
  source_file_offset BIGINT
  );

CREATE TABLE kills_by_ghosts (
  killed_player VARCHAR(20) NOT NULL,
  killed_start_time DATETIME NOT NULL,
  killer VARCHAR(20) NOT NULL
  );

CREATE TABLE kills_of_ghosts (
  player VARCHAR(20),
  start_time DATETIME,
  ghost VARCHAR(20)
  );

CREATE TABLE kills_of_uniques (
  player VARCHAR(20) NOT NULL,
  kill_time DATETIME NOT NULL,
  monster VARCHAR(20),
  FOREIGN KEY (player) REFERENCES players (name)
  );

CREATE INDEX kill_uniq_pmons ON kills_of_uniques (player, monster);

CREATE TABLE kunique_turns (
  player VARCHAR(20) NOT NULL,
  start_time DATETIME NOT NULL,
  monster VARCHAR(20),
  turn INT,
  FOREIGN KEY (player) REFERENCES players (name)
  );
CREATE INDEX kill_uniq_pgameturn ON kunique_turns (player, start_time);

-- Keep track of who's killed how many uniques, and when they achieved this.
CREATE TABLE kunique_times (
  player VARCHAR(20) PRIMARY KEY,
  -- Number of distinct uniques slain.
  nuniques INT DEFAULT 0 NOT NULL,
  -- When this number was reached.
  kill_time DATETIME NOT NULL,
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );

CREATE TABLE rune_finds (
  player VARCHAR(20),
  start_time DATETIME,
  rune_time DATETIME,
  rune VARCHAR(20),
  xl INT,
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );
CREATE INDEX rune_finds_p ON rune_finds (player, rune);

CREATE TABLE branch_enters (
  player VARCHAR(20),
  start_time DATETIME,
  mile_time DATETIME,
  br VARCHAR(20),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );
CREATE INDEX branch_enters_p ON branch_enters (player, br);

CREATE TABLE branch_ends (
  player VARCHAR(20),
  start_time DATETIME,
  mile_time DATETIME,
  br VARCHAR(20),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );
CREATE INDEX branch_ends_p ON branch_ends (player, br);

CREATE TABLE ziggurats (
  player VARCHAR(20),
  deepest INT NOT NULL,
  place VARCHAR(10) NOT NULL,
  zig_time DATETIME NOT NULL,
  -- Game start time, with player name can be used to locate the relevant game.
  start_time DATETIME NOT NULL,
  FOREIGN KEY (player) REFERENCES players (name)
  );
CREATE INDEX ziggurat_depths ON ziggurats (deepest, zig_time);

CREATE TABLE active_streaks (
  player VARCHAR(20) PRIMARY KEY,
  streak MEDIUMINT DEFAULT 1,
  streak_time DATETIME NOT NULL,
  FOREIGN KEY (player) REFERENCES players (name)
  );

-- Generated table to keep track of the last milestone for each player/server.
CREATE TABLE whereis_table (
  player VARCHAR(20),
  src CHAR(3),
  start_time DATETIME NOT NULL,
  mile_time DATETIME NOT NULL,
  PRIMARY KEY (player, src),
  FOREIGN KEY (player) REFERENCES players (name)
  );

-- Generated table to keep track of the last game finished for each player/server.
CREATE TABLE last_game_table (
  player VARCHAR(20),
  src CHAR(3),
  start_time DATETIME NOT NULL,
  PRIMARY KEY (player, src),
  FOREIGN KEY (player) REFERENCES players (name)
  );

-- Generated table to keep track of streaks for each player.
CREATE TABLE streaks (
  player VARCHAR(20) PRIMARY KEY,
  -- Because you just know Stabwound's going to win 128 in a row
  streak MEDIUMINT NOT NULL,
  streak_time DATETIME NOT NULL,
  FOREIGN KEY (player) REFERENCES players (name)
  );

CREATE TABLE player_won_gods (
  player VARCHAR(20),
  win_time DATETIME,
  god VARCHAR(20),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
);
CREATE INDEX player_won_gods_pg ON player_won_gods (player, god);

CREATE TABLE player_max_piety (
  player VARCHAR(20),
  god VARCHAR(20),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
);
CREATE INDEX player_max_piety_pg ON player_max_piety (player, god);

-- Audit table for point assignment. Tracks both permanent and
-- temporary points.

CREATE TABLE player_points (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  player VARCHAR(20) NOT NULL,
  temp BOOLEAN DEFAULT 0,
  points MEDIUMINT NOT NULL DEFAULT 0,
  team_points MEDIUMINT NOT NULL DEFAULT 0,
  point_source VARCHAR(150) NOT NULL,
  FOREIGN KEY (player) REFERENCES players (name)
  );

CREATE INDEX point_player_src ON player_points (player, point_source);

-- Clan point assignments.
CREATE TABLE clan_points (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  captain VARCHAR(20) NOT NULL,
  points MEDIUMINT NOT NULL DEFAULT 0,
  point_source VARCHAR(150) NOT NULL,
  FOREIGN KEY (captain) REFERENCES players (name)
  );

CREATE TABLE deaths_to_uniques (
  player  VARCHAR(20),
  uniq    VARCHAR(50),
  start_time DATETIME,
  end_time   DATETIME,
  FOREIGN KEY (player) REFERENCES players (name)
  );
CREATE INDEX deaths_to_uniques_p ON deaths_to_uniques (player);

CREATE TABLE deaths_to_distinct_uniques (
  player VARCHAR(20),
  ndeaths INT,
  death_time DATETIME,
  PRIMARY KEY (player),
  FOREIGN KEY (player) REFERENCES players (name)
  );
CREATE INDEX deaths_to_distinct_uniques_p
ON deaths_to_distinct_uniques (player, ndeaths);

CREATE TABLE player_maxed_skills (
  player VARCHAR(20),
  skill VARCHAR(25),
  PRIMARY KEY (player, skill),
  FOREIGN KEY (player) REFERENCES players (name)
  );
CREATE INDEX player_maxed_sk ON player_maxed_skills (player, skill);

CREATE TABLE player_fifteen_skills (
  player VARCHAR(20),
  skill VARCHAR(25),
  PRIMARY KEY (player, skill),
  FOREIGN KEY (player) REFERENCES players (name)
  );
CREATE INDEX player_fifteen_sk ON player_fifteen_skills (player, skill);

-- Tracks banners won by each player. Banners (badges?) are permanent
-- decorations, so once a player has earned a banner, there's no need to
-- check it again.
CREATE TABLE player_banners (
  player VARCHAR(20),
  banner VARCHAR(50),
  prestige INT NOT NULL,
  temp BOOLEAN,
  PRIMARY KEY (player, banner),
  FOREIGN KEY (player) REFERENCES players (name)
  );
CREATE INDEX player_banners_player ON player_banners (player);

CREATE TABLE clan_banners (
  team_captain VARCHAR(20),
  banner VARCHAR(50),
  prestige INT NOT NULL,
  PRIMARY KEY (team_captain, banner),
  FOREIGN KEY (team_captain) REFERENCES players (name)
);
CREATE INDEX clan_banners_captain ON clan_banners (team_captain);

-- Views for trophies

-- The three fastest realtime wins. Ties are broken by who got there first.
CREATE VIEW fastest_realtime AS
SELECT id, player, duration
  FROM games
 WHERE killertype = 'winning'
 ORDER BY duration, end_time
 LIMIT 3;

-- The three fastest realtime allrune wins. Ties are broken by who got there first.
CREATE VIEW fastest_realtime_allruner AS
SELECT id, player, duration
  FROM games
 WHERE killertype = 'winning' AND runes = 15
 ORDER BY duration, end_time
 LIMIT 3;

-- If there's a tie on start time, break it by seeing which game finished first.
CREATE VIEW last_started_win AS
SELECT *
  FROM games
 WHERE killertype = 'winning'
ORDER BY start_time DESC, end_time LIMIT 1;

-- The three fastest wins (turncount)
CREATE VIEW fastest_turncount AS
SELECT id, player, turn
  FROM games
 WHERE killertype = 'winning'
ORDER BY turn, end_time
LIMIT 3;

CREATE VIEW most_pacific_wins AS
SELECT id, player, kills
  FROM games
 WHERE killertype = 'winning' AND kills IS NOT NULL
ORDER BY kills
 LIMIT 3;

CREATE VIEW clan_combo_highscores AS
SELECT p.team_captain, g.*
FROM combo_highscores g, players p
WHERE g.player = p.name
AND p.team_captain IS NOT NULL;

CREATE VIEW combo_hs_clan_scoreboard AS
SELECT team_captain, COUNT(*) AS combos
FROM clan_combo_highscores
GROUP BY team_captain
ORDER BY combos DESC
LIMIT 20;

CREATE VIEW clan_total_scores AS
SELECT team_captain, (SUM(score_full) + SUM(team_score_full) - SUM(player_score_only)) score
FROM players
WHERE team_captain IS NOT NULL
GROUP BY team_captain
ORDER BY score DESC;

CREATE VIEW clan_dated_unique_kills AS
SELECT p.team_captain AS team_captain, k.monster AS monster, 
                  MIN(k.kill_time) AS first_time
FROM  players p INNER JOIN kills_of_uniques k
                       ON p.name = k.player
WHERE p.team_captain IS NOT NULL
GROUP BY p.team_captain, k.monster;

CREATE VIEW clan_unique_kills AS
SELECT team_captain, COUNT(*) AS kills, MAX(first_time) AS end_time
FROM clan_dated_unique_kills
GROUP BY team_captain
ORDER BY kills DESC, end_time
LIMIT 10;

CREATE VIEW game_combo_win_highscores AS
SELECT *
FROM combo_highscores
WHERE killertype = 'winning';

CREATE VIEW combo_hs_scoreboard AS
SELECT player, COUNT(*) AS nscores
FROM combo_highscores
GROUP BY player
ORDER BY nscores DESC
LIMIT 20;

CREATE VIEW streak_scoreboard AS
SELECT player, streak
FROM streaks
ORDER BY streak DESC, streak_time
LIMIT 3;

CREATE VIEW best_ziggurat_dives AS
SELECT player, deepest, place, zig_time, start_time
  FROM ziggurats
ORDER BY deepest DESC, zig_time
LIMIT 3;

CREATE VIEW youngest_rune_finds AS
SELECT player, rune, start_time, rune_time, xl
  FROM rune_finds
 WHERE rune != 'abyssal' AND rune != 'slimy'
ORDER BY xl, rune_time
 LIMIT 5;

CREATE VIEW most_deaths_to_uniques AS
SELECT player, ndeaths, death_time
  FROM deaths_to_distinct_uniques
ORDER BY ndeaths DESC, death_time
 LIMIT 3;

CREATE VIEW all_hellpan_kills AS
SELECT player, COUNT(DISTINCT monster) AS hellpan_kills
  FROM kills_of_uniques
 WHERE monster = 'Antaeus' OR monster = 'Asmodeus' OR monster = 'Cerebov' OR
       monster = 'Dispater' OR monster = 'Ereshkigal' OR 
       monster = 'Gloorx Vloq' OR monster = 'Lom Lobon' OR monster = 'Mnoleg'
GROUP BY player
  HAVING hellpan_kills >= 8;

CREATE VIEW fivefives_nine AS
SELECT player, COUNT(DISTINCT MID(charabbrev,1,2)) AS race_count,
               COUNT(DISTINCT MID(charabbrev,3,2)) AS class_count
FROM games
WHERE xl>=9
GROUP BY player
HAVING race_count >= 5 AND class_count >= 5;

CREATE VIEW fivefives_rune AS
SELECT player, COUNT(DISTINCT MID(charabbrev,1,2)) AS race_count,
               COUNT(DISTINCT MID(charabbrev,3,2)) AS class_count
FROM milestones
WHERE verb = 'rune'
GROUP BY player
HAVING race_count >= 5 AND class_count >= 5;

CREATE VIEW fivefives_win AS
SELECT player, COUNT(DISTINCT MID(charabbrev,1,2)) AS race_count,
               COUNT(DISTINCT MID(charabbrev,3,2)) AS class_count
FROM games
WHERE killertype = 'winning'
GROUP BY player
HAVING race_count >= 5 AND class_count >= 5;

CREATE VIEW orbrun_tomb AS
SELECT r.player, COUNT(*) AS orbrun_tomb_count
  FROM (milestones r INNER JOIN milestones o ON r.start_time = o.start_time)
                     INNER JOIN milestones b ON r.start_time = b.start_time
 WHERE r.verb = 'rune'
   AND r.noun = 'golden'
   AND o.verb = 'orb'
   AND b.verb = 'br.enter'
   AND b.noun = 'Tomb'
   AND r.turn > o.turn
   AND b.turn > o.turn
   AND r.player = o.player
   AND o.player = b.player
   AND NOT r.noun = 'abyssal'
GROUP BY r.player
  HAVING orbrun_tomb_count >= 1
ORDER BY orbrun_tomb_count DESC;

CREATE VIEW have_hellpan_kills AS
SELECT h.player, COUNT(*) AS hellpan_kills
  FROM kills_of_uniques h INNER JOIN kills_of_uniques p ON h.player = p.player
 WHERE (h.monster = 'Antaeus' OR h.monster = 'Asmodeus' OR 
        h.monster = 'Dispater' OR h.monster = 'Ereshkigal')
   AND (p.monster = 'Cerebov' OR p.monster = 'Gloorx Vloq' OR 
        p.monster = 'Lom Lobon' OR p.monster = 'Mnoleg')
GROUP BY h.player
  HAVING hellpan_kills >= 1;

CREATE VIEW nearby_uniques AS
SELECT f.player, f.monster, s.monster AS smonster, f.turn, s.turn AS sturn
  FROM kunique_turns f INNER JOIN kunique_turns s ON f.player = s.player
 WHERE f.start_time = s.start_time
   AND f.turn <= s.turn
   AND f.turn + 2 >= s.turn
   AND NOT f.monster = s.monster;