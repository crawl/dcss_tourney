-- Use InnoDB for transaction support?
-- SET storage_engine=InnoDB;

DROP TABLE IF EXISTS team_ranks;
DROP TABLE IF EXISTS player_ranks;
DROP TABLE IF EXISTS player_maxed_skills;
DROP TABLE IF EXISTS player_fifteen_skills;
DROP TABLE IF EXISTS clan_banners;
DROP TABLE IF EXISTS player_banners;
DROP TABLE IF EXISTS player_won_gods;
DROP TABLE IF EXISTS player_max_piety;
DROP TABLE IF EXISTS whereis_table;
DROP TABLE IF EXISTS last_game_table;
DROP TABLE IF EXISTS streaks;
DROP TABLE IF EXISTS ziggurats;
DROP TABLE IF EXISTS rune_finds;
DROP TABLE IF EXISTS branch_enters;
DROP TABLE IF EXISTS branch_ends;
DROP TABLE IF EXISTS kills_of_uniques;
DROP TABLE IF EXISTS kills_of_ghosts;
DROP TABLE IF EXISTS milestone_bookmark;
DROP TABLE IF EXISTS milestones;
DROP TABLE IF EXISTS combo_highscores;
DROP TABLE IF EXISTS class_highscores;
DROP TABLE IF EXISTS species_highscores;
DROP TABLE IF EXISTS player_nemelex_wins;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS players;

DROP VIEW IF EXISTS game_combo_win_highscores;
DROP VIEW IF EXISTS have_hellpan_kills;
DROP VIEW IF EXISTS all_hellpan_kills;
DROP VIEW IF EXISTS fivefives_rune;
DROP VIEW IF EXISTS fivefives_win;
DROP VIEW IF EXISTS orbrun_tomb;

DROP VIEW IF EXISTS clan_games;
DROP VIEW IF EXISTS wins;
DROP VIEW IF EXISTS first_wins;
DROP VIEW IF EXISTS allrune_wins;
DROP VIEW IF EXISTS first_allrune_wins;
DROP VIEW IF EXISTS highest_scores;
DROP VIEW IF EXISTS clan_highest_scores;
DROP VIEW IF EXISTS lowest_turncount_wins;
DROP VIEW IF EXISTS clan_lowest_turncount_wins;
DROP VIEW IF EXISTS fastest_wins;
DROP VIEW IF EXISTS clan_fastest_wins;
DROP VIEW IF EXISTS nonhep_wins;
DROP VIEW IF EXISTS low_xl_nonhep_wins;
DROP VIEW IF EXISTS player_god_usage;
DROP VIEW IF EXISTS player_piety_score;
DROP VIEW IF EXISTS clan_piety_score;
DROP VIEW IF EXISTS player_banner_score;
DROP VIEW IF EXISTS branch_enter_count;
DROP VIEW IF EXISTS branch_end_count;
DROP VIEW IF EXISTS scaled_rune_find_count;
DROP VIEW IF EXISTS exploration_union;
DROP VIEW IF EXISTS player_exploration_score;
DROP VIEW IF EXISTS clan_branch_enter_count;
DROP VIEW IF EXISTS clan_branch_end_count;
DROP VIEW IF EXISTS clan_scaled_rune_find_count;
DROP VIEW IF EXISTS clan_exploration_union;
DROP VIEW IF EXISTS clan_exploration_score;
DROP VIEW IF EXISTS unique_kill_count;
DROP VIEW IF EXISTS ghost_kill_count;
DROP VIEW IF EXISTS harvest_union;
DROP VIEW IF EXISTS player_harvest_score;
DROP VIEW IF EXISTS clan_unique_kill_count;
DROP VIEW IF EXISTS clan_ghost_kill_count;
DROP VIEW IF EXISTS clan_harvest_union;
DROP VIEW IF EXISTS clan_harvest_score;
DROP VIEW IF EXISTS player_nemelex_score;
DROP VIEW IF EXISTS player_combo_score;
DROP VIEW IF EXISTS clan_combo_score;
DROP VIEW IF EXISTS clan_streaks;
DROP VIEW IF EXISTS player_best_streak;
DROP VIEW IF EXISTS clan_best_streak;
DROP VIEW IF EXISTS player_win_perc;

CREATE TABLE IF NOT EXISTS players (
  name VARCHAR(20) PRIMARY KEY,
  team_captain VARCHAR(20),
  -- This is the computed score! We will overwrite it each time we
  -- recalculate it, and it may be null at any point.
  score_full DECIMAL(5,0),

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
  -- Source server
  src VARCHAR(10),

  player VARCHAR(20),
  start_time DATETIME,
  -- currently 64bit uint, but allow extra space for changes
  seed VARCHAR(255),
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
  ac INT,
  ev INT,
  god VARCHAR(20),
  duration INT,
  turn BIGINT,
  runes INT DEFAULT 0,
  killertype VARCHAR(20),
  killer CHAR(100),
  kgroup CHAR(100),
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

CREATE TABLE player_nemelex_wins AS
SELECT * FROM games;
ALTER TABLE player_nemelex_wins DROP COLUMN id;
CREATE INDEX nem_player ON player_nemelex_wins (player, charabbrev);

CREATE TABLE milestones (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  -- Source milestone file
  source_file VARCHAR(150),
  -- Source server
  src VARCHAR(10),

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
  scrolls_used INT,
  potions_used INT,
  god VARCHAR(50),
  duration BIGINT,
  turn BIGINT,
  runes INT,
  nrune INT,
  zigscompleted INT,

  -- Game start time.
  start_time DATETIME,

  -- Milestone time.
  milestone_time DATETIME,

  -- Known milestones: abyss.enter, abyss.exit, rune, orb, ghost, uniq,
  -- uniq.ban, br.enter, br.end, br.exit.
  verb VARCHAR(20),
  noun VARCHAR(200),

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

CREATE TABLE kills_of_ghosts (
  player VARCHAR(20),
  start_time DATETIME,
  ghost VARCHAR(100)
  );

CREATE TABLE kills_of_uniques (
  player VARCHAR(20) NOT NULL,
  kill_time DATETIME NOT NULL,
  monster VARCHAR(20),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );

CREATE INDEX kill_uniq_pmons ON kills_of_uniques (player, monster);

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
  completed INT NOT NULL,
  deepest INT NOT NULL,
  place VARCHAR(10) NOT NULL,
  zig_time DATETIME NOT NULL,
  -- Game start time, with player name can be used to locate the relevant game.
  start_time DATETIME NOT NULL,
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );
CREATE INDEX ziggurat_depths ON ziggurats (completed, deepest);

-- Generated table to keep track of the last milestone for each player/server.
CREATE TABLE whereis_table (
  player VARCHAR(20),
  src CHAR(3),
  start_time DATETIME NOT NULL,
  mile_time DATETIME NOT NULL,
  PRIMARY KEY (player, src),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );

-- Generated table to keep track of the last game finished for each player/server.
CREATE TABLE last_game_table (
  player VARCHAR(20),
  src CHAR(3),
  start_time DATETIME NOT NULL,
  PRIMARY KEY (player, src),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );

CREATE TABLE player_won_gods (
  player VARCHAR(20),
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

-- Track current streak lengths so they can be easily accessed for ranking
-- purposes; full streak info is not cached.
CREATE TABLE streaks (
  player VARCHAR(20),
  src CHAR(3),
  start_time DATETIME NOT NULL,
  length INT,
  PRIMARY KEY (player, src, start_time),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
);

-- Player ranking in various categories; in principle this can
-- all be achieved from the extant database, but requires the RANK() window
-- function on a large join, so we cache it here.
CREATE TABLE player_ranks (
  player VARCHAR(20),
  nonrep_wins INT,
  first_win INT,
  first_allrune_win INT,
  streak INT,
  highest_score INT,
  lowest_turncount_win INT,
  fastest_win INT,
  low_xl_win INT,
  win_perc INT,
  piety INT,
  banner_score INT,
  exploration INT,
  harvest INT,
  combo_score INT,
  nemelex_score INT,
  ziggurat_dive INT,
  PRIMARY KEY (player),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
);

CREATE TABLE team_ranks (
  team_captain VARCHAR(20) NOT NULL,
  nonrep_wins INT,
  streak INT,
  highest_score INT,
  lowest_turncount_win INT,
  fastest_win INT,
  piety INT,
  harvest INT,
  exploration INT,
  combo_score INT,
  nemelex_score INT,
  ziggurat_dive INT,
  banner_score INT,
  PRIMARY KEY (team_captain),
  FOREIGN KEY (team_captain) REFERENCES teams (owner) ON DELETE CASCADE
);


CREATE TABLE player_maxed_skills (
  player VARCHAR(20),
  skill VARCHAR(25),
  PRIMARY KEY (player, skill),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );
CREATE INDEX player_maxed_sk ON player_maxed_skills (player, skill);

CREATE TABLE player_fifteen_skills (
  player VARCHAR(20),
  skill VARCHAR(25),
  PRIMARY KEY (player, skill),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
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
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );
CREATE INDEX player_banners_player ON player_banners (player);

CREATE TABLE clan_banners (
  team_captain VARCHAR(20),
  banner VARCHAR(50),
  prestige INT NOT NULL,
  PRIMARY KEY (team_captain, banner),
  -- is cascade correct here?
  FOREIGN KEY (team_captain) REFERENCES players (name) ON DELETE CASCADE
);
CREATE INDEX clan_banners_captain ON clan_banners (team_captain);

-- Views for trophies

CREATE VIEW game_combo_win_highscores AS
SELECT *
FROM combo_highscores
WHERE killertype = 'winning';

CREATE VIEW all_hellpan_kills AS
SELECT player, COUNT(DISTINCT monster) AS hellpan_kills
  FROM kills_of_uniques
 WHERE monster = 'Antaeus' OR monster = 'Asmodeus' OR monster = 'Cerebov' OR
       monster = 'Dispater' OR monster = 'Ereshkigal' OR
       monster = 'Gloorx Vloq' OR monster = 'Lom Lobon' OR
       monster = 'Mnoleg' OR monster = 'the Serpent of Hell'
GROUP BY player
  HAVING hellpan_kills >= 9;

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

-- These views inner join on clan info for clan rankings. Sadly mysql's query
-- optimizer will not skip a specified join, even in the case of an eq_ref
-- inner join where the joined on columns aren't used in the outer select.

-- If we run into performance issues in generating player ranks we'll need to
-- split out clan and player queries, however the clan join is still needed
-- for clan ranking so the savings won't be much.
CREATE VIEW clan_games AS
SELECT g.*, p.team_captain
  FROM games AS g INNER JOIN players AS p ON g.player = p.name;

CREATE VIEW wins AS
SELECT *
  FROM clan_games
  WHERE killertype = 'winning';

CREATE VIEW first_wins AS
SELECT g.* FROM wins AS g
  LEFT OUTER JOIN wins AS g2
  ON g.player = g2.player AND g.end_time > g2.end_time
  WHERE g2.end_time IS NULL;

CREATE VIEW allrune_wins AS
SELECT * FROM wins WHERE killertype = 'winning' AND runes = 15;

CREATE VIEW first_allrune_wins AS
SELECT g.* FROM
  allrune_wins AS g
  LEFT OUTER JOIN allrune_wins AS g2
  ON g.player = g2.player AND g.end_time > g2.end_time
  WHERE g2.end_time IS NULL;

CREATE VIEW highest_scores AS
SELECT g.* FROM games AS g
  LEFT OUTER JOIN games AS g2 ON g.player = g2.player AND g.score < g2.score
  WHERE g2.score IS NULL AND g.score > 0;

CREATE VIEW clan_highest_scores AS
SELECT g.* FROM clan_games AS g
  LEFT OUTER JOIN clan_games AS g2
    ON g.team_captain = g2.team_captain AND g.score < g2.score
  WHERE g2.score IS NULL AND g.score > 0;

CREATE VIEW lowest_turncount_wins AS
SELECT g.* FROM wins AS g
  LEFT OUTER JOIN wins AS g2
  ON g.player = g2.player AND g.turn > g2.turn
  WHERE g2.turn IS NULL;

CREATE VIEW clan_lowest_turncount_wins AS
SELECT g.* FROM wins AS g
  LEFT OUTER JOIN wins AS g2
  ON g.team_captain = g2.team_captain AND g.turn > g2.turn
  WHERE g2.turn IS NULL;

CREATE VIEW fastest_wins AS
SELECT g.* FROM wins AS g
  LEFT OUTER JOIN wins AS g2
  ON g.player = g2.player AND g.duration > g2.duration
  WHERE g2.duration IS NULL;

CREATE VIEW clan_fastest_wins AS
SELECT g.* FROM wins AS g
  LEFT OUTER JOIN wins AS g2
  ON g.team_captain = g2.team_captain AND g.duration > g2.duration
  WHERE g2.duration IS NULL;

CREATE VIEW nonhep_wins AS
SELECT * FROM wins AS g
  WHERE NOT EXISTS (SELECT m.id FROM milestones AS m
                        WHERE m.game_id = g.id
                        AND (verb = 'god.renounce' OR verb='god.worship')
                        AND NOUN = 'Hepliaklqana');

CREATE VIEW low_xl_nonhep_wins AS
SELECT g.* FROM nonhep_wins AS g
  LEFT OUTER JOIN nonhep_wins AS g2
  ON g.player = g2.player AND g.xl > g2.xl
  WHERE g2.xl IS NULL AND g.xl < 27;

CREATE VIEW player_win_perc AS
SELECT player,
  CAST( (SUM(killertype='winning') / (COUNT(*) + 1.0)) * 100.0 AS DECIMAL(5,2))
  AS win_perc FROM games GROUP BY player;

-- My kingdom for a full join. Correct handling for Gozag, Xom, and No God
CREATE VIEW player_god_usage AS
SELECT mp.player, mp.god AS max_piety, wg.god AS won
  FROM player_max_piety AS mp
  LEFT OUTER JOIN player_won_gods AS wg
    ON mp.player = wg.player AND mp.god = wg.god 
UNION ALL
SELECT wg.player, mp.god AS max_piety, wg.god AS won
  FROM player_max_piety AS mp
  RIGHT OUTER JOIN player_won_gods AS wg
    ON mp.player = wg.player AND mp.god = wg.god
  WHERE mp.god IS NULL;

CREATE VIEW player_piety_score AS
SELECT player, COUNT(DISTINCT max_piety) AS champion,
	  COUNT(DISTINCT won) AS won,
	  COUNT(DISTINCT max_piety) + COUNT(DISTINCT won) AS piety
  FROM player_god_usage
  GROUP BY player;

CREATE VIEW clan_piety_score AS
SELECT p.team_captain, COUNT(DISTINCT g.max_piety) AS champion,
	  COUNT(DISTINCT g.won) AS won,
	  COUNT(DISTINCT g.max_piety) + COUNT(DISTINCT g.won) AS piety
  FROM player_god_usage AS g INNER JOIN players AS p ON g.player = p.name
  GROUP BY p.team_captain;

CREATE VIEW player_banner_score AS
SELECT player, SUM(IF(prestige = 3, 4, prestige)) AS bscore,
       GROUP_CONCAT(CONCAT(banner, ' ', prestige) SEPARATOR ',') AS banners
  FROM player_banners WHERE temp = false GROUP BY player;

CREATE VIEW branch_enter_count AS
SELECT player, COUNT(DISTINCT br) AS score FROM branch_enters GROUP BY player;

CREATE VIEW clan_branch_enter_count AS
SELECT p.team_captain, COUNT(DISTINCT br) AS score
  FROM branch_enters AS b INNER JOIN players AS p ON b.player = p.name
  GROUP BY p.team_captain;

CREATE VIEW branch_end_count AS
SELECT player, COUNT(DISTINCT br) AS score FROM branch_ends GROUP BY player;

CREATE VIEW clan_branch_end_count AS
SELECT p.team_captain, COUNT(DISTINCT br) AS score
  FROM branch_ends AS b INNER JOIN players AS p ON b.player = p.name
  GROUP BY p.team_captain;

CREATE VIEW scaled_rune_find_count AS
SELECT player, 3*COUNT(DISTINCT rune) AS score FROM rune_finds GROUP BY player;

CREATE VIEW clan_scaled_rune_find_count AS
SELECT p.team_captain, 3*COUNT(DISTINCT r.rune) AS score
  FROM rune_finds AS r INNER JOIN players AS p ON r.player = p.name
  GROUP BY player;

CREATE VIEW exploration_union AS
SELECT player, score AS score
  FROM branch_enter_count
  UNION ALL SELECT player, score FROM branch_end_count
  UNION ALL SELECT player, score FROM scaled_rune_find_count;

CREATE VIEW clan_exploration_union AS
SELECT team_captain, score
  FROM clan_branch_enter_count
  UNION ALL SELECT team_captain, score FROM clan_branch_end_count
  UNION ALL SELECT team_captain, score FROM clan_scaled_rune_find_count;

-- Can't use a join here because of (starting) abyss shenanigains
-- and there's no full outer join
CREATE VIEW player_exploration_score AS
SELECT player, SUM(score) AS score
  FROM exploration_union GROUP BY player;

CREATE VIEW clan_exploration_score AS
SELECT team_captain, SUM(score) AS score
  FROM clan_exploration_union WHERE team_captain IS NOT NULL
  GROUP BY team_captain;

CREATE VIEW unique_kill_count AS
SELECT player, COUNT(DISTINCT monster) AS score
  FROM kills_of_uniques GROUP BY player;

CREATE VIEW clan_unique_kill_count AS
SELECT p.team_captain, COUNT(DISTINCT u.monster) AS score
  FROM kills_of_uniques AS u INNER JOIN players AS p
    ON u.player = p.name
  GROUP BY p.team_captain;

CREATE VIEW ghost_kill_count AS
SELECT player, COUNT(*) AS score FROM kills_of_ghosts GROUP BY player;

CREATE VIEW clan_ghost_kill_count AS
SELECT p.team_captain, COUNT(*) AS score
  FROM kills_of_ghosts AS u INNER JOIN players AS p
    ON u.player = p.name
  GROUP BY p.team_captain;

CREATE VIEW harvest_union AS
SELECT player, score FROM unique_kill_count
UNION ALL SELECT player, score FROM ghost_kill_count;

CREATE VIEW clan_harvest_union AS
SELECT team_captain, score FROM clan_unique_kill_count
UNION ALL SELECT team_captain, score FROM clan_ghost_kill_count;

-- Can't use a join because a player could have one but not the other
-- and there's no full outer join
CREATE VIEW player_harvest_score AS
SELECT player, SUM(score) AS score
  FROM harvest_union
  GROUP BY player;

CREATE VIEW clan_harvest_score AS
SELECT team_captain, SUM(score) AS score
  FROM clan_harvest_union
  GROUP BY team_captain;

CREATE VIEW player_combo_score AS
SELECT c.player AS player,
       COUNT(*) + COUNT(c.killertype='winning')
                 + 3 * COUNT(sp.raceabbr) + 3 * COUNT(cl.class) AS total,
       COUNT(*) AS combos,
       COUNT(c.killertype='winning') AS won_combos,
       COUNT(sp.raceabbr) AS sp_hs, COUNT(cl.class) AS cls_hs
  FROM combo_highscores AS c
  LEFT OUTER JOIN species_highscores AS sp
    ON c.player = sp.player AND c.charabbrev = sp.charabbrev
  LEFT OUTER JOIN class_highscores AS cl
    ON c.player = cl.player AND c.charabbrev = cl.charabbrev
  GROUP BY c.player;

CREATE VIEW clan_combo_score AS
SELECT p.team_captain,
       COUNT(*) + COUNT(c.killertype='winning')
                 + 3 * COUNT(sp.raceabbr) + 3 * COUNT(cl.class) AS total,
       COUNT(*) AS combos,
       COUNT(c.killertype='winning') AS won_combos,
       COUNT(sp.raceabbr) AS sp_hs, COUNT(cl.class) AS cls_hs
  FROM combo_highscores AS c
  LEFT OUTER JOIN species_highscores AS sp
    ON c.player = sp.player AND c.charabbrev = sp.charabbrev
  LEFT OUTER JOIN class_highscores AS cl
    ON c.player = cl.player AND c.charabbrev = cl.charabbrev
  INNER JOIN players AS p
    ON c.player = p.name
  WHERE p.team_captain IS NOT NULL GROUP BY p.team_captain;

CREATE VIEW player_nemelex_score AS
SELECT player, COUNT(DISTINCT charabbrev) AS score FROM player_nemelex_wins
GROUP BY player;

CREATE VIEW player_best_streak AS
SELECT s.player, s.length FROM streaks AS s
  LEFT OUTER JOIN streaks AS s2
    ON s.player = s2.player AND s.length < s2.length
  WHERE s2.length IS NULL;

CREATE VIEW clan_streaks AS
SELECT p.team_captain, s.player, s.length
FROM streaks AS s INNER JOIN players AS p ON s.player = p.name
WHERE p.team_captain IS NOT NULL;

CREATE VIEW clan_best_streak AS
SELECT s.team_captain, s.player, s.length
FROM clan_streaks AS s
  LEFT OUTER JOIN clan_streaks AS s2
    ON s.team_captain = s2.team_captain AND s.length < s2.length
  WHERE s2.length IS NULL AND s.team_captain IS NOT NULL;
