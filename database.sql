drop table players;
drop table games;
drop table kills_by_ghosts;
drop table kills_of_ghosts;
drop table kills_of_uniques;
drop table rune_finds;


create table players (name char(20), team varchar(255), score_base bigint, team_score_base bigint);
alter table players add primary key playername (name);
create table games (
	player char(20), 
	start_time datetime, 
	score bigint,
	race char(10), 
	class char(10), 
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
	runes int, 
	killertype char(20), 
	killer char(20), 
        kaux char(255),
	damage int, 
	piety int,
        penitence int, 
	end_time datetime, 
	terse_msg varchar(255), 
	verb_msg varchar(255),
        nrune int
	);

alter table games add primary key game (player, start_time);

create table kills_by_ghosts (killed_player char(20), killed_start_time datetime, killer char(20));

create table kills_of_ghosts (player char(20), start_time datetime, ghost char(20));

create table kills_of_uniques (player char(20), monster char(20));

create table rune_finds (player char(20), start_time datetime, rune char(20));