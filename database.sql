DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS team_owners;
DROP TABLE IF EXISTS milestone_bookmark;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS kills_by_ghosts;
DROP TABLE IF EXISTS kills_of_ghosts;
DROP TABLE IF EXISTS kills_of_uniques;
DROP TABLE IF EXISTS rune_finds;

CREATE TABLE teams (id MEDIUMINT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL);

CREATE TABLE players (
  name CHAR(20) PRIMARY KEY,
  team MEDIUMINT,
  score_base BIGINT,
  team_score_base BIGINT,
  FOREIGN KEY (team) REFERENCES teams (id) ON DELETE SET NULL);

-- Mapping table linking teams and their owners.
CREATE TABLE team_owners (
  team MEDIUMINT,
  owner CHAR(20),
  PRIMARY KEY (team, owner),
  FOREIGN KEY (team) REFERENCES teams (id) ON DELETE CASCADE,
  FOREIGN KEY (owner) REFERENCES players (name) ON DELETE CASCADE);

-- For mappings of logfile fields to columns, see loaddb.py
CREATE TABLE games (
    -- Source logfile
    source_file varchar(150),
    -- Offset in the source file.
    source_file_offset bigint,

	player char(20), 
	start_time datetime, 
	score bigint,
	race char(20),
	class char(20),
	version char(10), 
	lv char(8),
	uid int, 
	charabbrev char(4), 
	xl int, 
	skill char(16), 
	sk_lev int, 
	title varchar(255), 
	place char(16), 
	branch char(16), 
	lvl int, 
	ltyp char(16), 
	hp int, 
	maxhp int,
 	maxmaxhp int, 
	strength int, 
	intellegence int, 
	dexterity int, 
	god char(20), 
	duration int, 
	turn bigint,
	runes int DEFAULT 0,
	killertype char(20),
	killer char(50),
        kaux varchar(255),
	damage int,
	piety int,
        penitence int, 
	end_time datetime, 
	terse_msg varchar(255), 
	verb_msg varchar(255),
        nrune int DEFAULT 0,

    CONSTRAINT PRIMARY KEY (source_file, source_file_offset)
	);

-- A table to keep track of the last milestone we've processed. This
-- will have only one row for one filename.
CREATE TABLE milestone_bookmark (source_file VARCHAR(150) PRIMARY KEY, source_file_offset BIGINT);

create table kills_by_ghosts (
    killed_player char(20) NOT NULL,
    killed_start_time datetime NOT NULL,
    killer char(20) NOT NULL
    );

create table kills_of_ghosts (player char(20), start_time datetime, ghost char(20));

create table kills_of_uniques (
player char(20) NOT NULL,
monster char(20)
);

create table rune_finds (player char(20), start_time datetime, rune char(20));
