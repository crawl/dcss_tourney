drop table if exists players;
drop table if exists milestone_bookmark;
drop table if exists games;
drop table if exists kills_by_ghosts;
drop table if exists kills_of_ghosts;
drop table if exists kills_of_uniques;
drop table if exists rune_finds;

create table players (name char(20), team varchar(255), score_base bigint, team_score_base bigint);
alter table players add primary key playername (name);

-- For mappings of logfile fields to columns, see loaddb.py
create table games (
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
