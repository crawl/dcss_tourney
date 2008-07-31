DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS team_owners;
DROP TABLE IF EXISTS milestone_bookmark;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS kills_by_ghosts;
DROP TABLE IF EXISTS kills_of_ghosts;
DROP TABLE IF EXISTS kills_of_uniques;
DROP TABLE IF EXISTS rune_finds;

CREATE TABLE IF NOT EXISTS players (
  name CHAR(20) PRIMARY KEY,
  team_captain CHAR(20),
  score_base BIGINT,
  team_score_base BIGINT,
  FOREIGN KEY (team_captain) REFERENCES players (name)
  ON DELETE SET NULL
  );

CREATE TABLE teams (
  owner CHAR(20) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (owner, name),
  FOREIGN KEY (owner) REFERENCES players (name)
  ON DELETE CASCADE
  );

-- Mapping table linking teams and their owners.
CREATE TABLE team_owners (
  owner CHAR(20),
  team MEDIUMINT,
  PRIMARY KEY (owner),
  FOREIGN KEY (team) REFERENCES teams (id) ON DELETE CASCADE,
  FOREIGN KEY (owner) REFERENCES players (name) ON DELETE CASCADE
  );

-- For mappings of logfile fields to columns, see loaddb.py
CREATE TABLE games (
  -- Source logfile
  source_file VARCHAR(150),
  -- Offset in the source file.
  source_file_offset BIGINT,

  player CHAR(20),
  start_time DATETIME,
  score BIGINT,
  race CHAR(20),
  class CHAR(20),
  version CHAR(10),
  lv CHAR(8),
  uid INT,
  charabbrev CHAR(4),
  xl INT,
  skill CHAR(16),
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
  intellegence INT,
  dexterity INT,
  god CHAR(20),
  duration INT,
  turn BIGINT,
  runes INT DEFAULT 0,
  killertype CHAR(20),
  killer CHAR(50),
  kaux VARCHAR(255),
  damage INT,
  piety INT,
  penitence INT,
  end_time DATETIME,
  terse_msg VARCHAR(255),
  verb_msg VARCHAR(255),
  nrune INT DEFAULT 0,

  CONSTRAINT PRIMARY KEY (source_file, source_file_offset)
  );

-- A table to keep track of the last milestone we've processed. This
-- will have only one row for one filename.
CREATE TABLE milestone_bookmark (
  source_file VARCHAR(150) PRIMARY KEY,
  source_file_offset BIGINT
  );

CREATE TABLE kills_by_ghosts (
  killed_player CHAR(20) NOT NULL,
  killed_start_time DATETIME NOT NULL,
  killer CHAR(20) NOT NULL
  );

CREATE TABLE kills_of_ghosts (
  player CHAR(20),
  start_time DATETIME,
  ghost CHAR(20)
  );

CREATE TABLE kills_of_uniques (
  player CHAR(20) NOT NULL,
  kill_time DATETIME NOT NULL,
  monster CHAR(20)
  );

CREATE TABLE rune_finds (
  player CHAR(20),
  start_time DATETIME,
  rune CHAR(20),
  FOREIGN KEY (player) REFERENCES players (name) ON DELETE CASCADE
  );