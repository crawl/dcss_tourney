-- Use InnoDB for transaction support?
-- SET storage_engine=InnoDB;

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

-- Player ranking in various categories; in principle this can all be achieved
-- from the extant database, but requires the DENSE_RANK() window function on a
-- large join, so we cache it here.
CREATE TABLE IF NOT EXISTS players (
  name VARCHAR(20) PRIMARY KEY,
  team_captain VARCHAR(20),
  -- These aare the computed scores! We will overwrite it each time we
  -- recalculate it, and it may be null at any point.
  score_full DECIMAL(7,0),
  nonrep_wins INT,
  first_win INT,
  first_allrune_win INT,
  streak INT,
  highest_score INT,
  lowest_turncount_win INT,
  fastest_win INT,
  most_pacific_win INT,
  win_perc INT,
  piety INT,
  banner_score INT,
  exploration INT,
  harvest INT,
  combo_score INT,
  nemelex_score INT,
  ziggurat_dive INT,
  FOREIGN KEY (team_captain) REFERENCES players (name)
  ON DELETE SET NULL
);

CREATE INDEX pscore ON players (score_full);

CREATE TABLE teams (
  owner VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  -- Clan scores, will be recomputed at intervals.
  total_score DECIMAL(7,0),
  nonrep_wins INT,
  streak INT,
  highest_score INT,
  lowest_turncount_win INT,
  fastest_win INT,
  most_pacific_win INT,
  piety INT,
  harvest INT,
  exploration INT,
  combo_score INT,
  nemelex_score INT,
  ziggurat_dive INT,
  banner_score INT,
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
  game_id BIGINT, -- warning: not implemented, should be removed or implemented.

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
  src VARCHAR(10),
  start_time DATETIME NOT NULL,
  mile_time DATETIME NOT NULL,
  PRIMARY KEY (player, src),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );

-- Generated table to keep track of the last game finished for each player/server.
CREATE TABLE last_game_table (
  player VARCHAR(20),
  src VARCHAR(10),
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

-- Track current best streaks so they can be easily accessed for ranking
-- and display purposes.
CREATE TABLE streaks (
  player VARCHAR(20),
  src VARCHAR(10),
  start_time DATETIME NOT NULL,
  length INT,
  streak_data JSON,
  PRIMARY KEY (player, src, start_time),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
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
