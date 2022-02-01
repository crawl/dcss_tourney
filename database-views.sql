-- Views for trophies

CREATE OR REPLACE VIEW game_combo_win_highscores AS
SELECT *
FROM combo_highscores
WHERE killertype = 'winning';

CREATE OR REPLACE VIEW all_hellpan_kills AS
SELECT player, COUNT(DISTINCT monster) AS hellpan_kills
  FROM kills_of_uniques
 WHERE monster = 'Antaeus' OR monster = 'Asmodeus' OR monster = 'Cerebov' OR
       monster = 'Dispater' OR monster = 'Ereshkigal' OR
       monster = 'Gloorx Vloq' OR monster = 'Lom Lobon' OR
       monster = 'Mnoleg' OR monster = 'the Serpent of Hell'
GROUP BY player
  HAVING hellpan_kills >= 9;

CREATE OR REPLACE VIEW fivefives_rune AS
SELECT player, COUNT(DISTINCT MID(charabbrev,1,2)) AS race_count,
               COUNT(DISTINCT MID(charabbrev,3,2)) AS class_count
FROM milestones
WHERE verb = 'rune'
GROUP BY player
HAVING race_count >= 5 AND class_count >= 5;

CREATE OR REPLACE VIEW fivefives_win AS
SELECT player, COUNT(DISTINCT MID(charabbrev,1,2)) AS race_count,
               COUNT(DISTINCT MID(charabbrev,3,2)) AS class_count
FROM games
WHERE killertype = 'winning'
GROUP BY player
HAVING race_count >= 5 AND class_count >= 5;

CREATE OR REPLACE VIEW orbrun_tomb AS
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

CREATE OR REPLACE VIEW have_hellpan_kills AS
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
CREATE OR REPLACE VIEW clan_games AS
SELECT g.*, p.team_captain
  FROM games AS g INNER JOIN players AS p ON g.player = p.name;

CREATE OR REPLACE VIEW wins AS
SELECT *
  FROM clan_games
  WHERE killertype = 'winning';

CREATE OR REPLACE VIEW first_wins AS
SELECT g.*, JSON_OBJECT('source_file', g.source_file,
                    'player', g.player,
		    'end_time', g.end_time,
		    'charabbrev', g.charabbrev) AS morgue_json  FROM wins AS g
  LEFT OUTER JOIN wins AS g2
  ON g.player = g2.player AND g.end_time > g2.end_time
  WHERE g2.end_time IS NULL;

CREATE OR REPLACE VIEW allrune_wins AS
SELECT * FROM wins WHERE killertype = 'winning' AND runes = 15;

CREATE OR REPLACE VIEW first_allrune_wins AS
SELECT g.*, JSON_OBJECT('source_file', g.source_file,
                    'player', g.player,
		    'end_time', g.end_time,
		    'charabbrev', g.charabbrev) AS morgue_json  FROM
  allrune_wins AS g
  LEFT OUTER JOIN allrune_wins AS g2
  ON g.player = g2.player AND g.end_time > g2.end_time
  WHERE g2.end_time IS NULL;

CREATE OR REPLACE VIEW highest_scores AS
SELECT g.*, JSON_OBJECT('source_file', g.source_file,
                    'player', g.player,
		    'end_time', g.end_time,
		    'charabbrev', g.charabbrev) AS morgue_json FROM games AS g
  LEFT OUTER JOIN games AS g2 ON g.player = g2.player AND g.score < g2.score
  WHERE g2.score IS NULL AND g.score > 0;

-- This is semantically the "clear description" of the clan_highest_scores
-- view. Best practice says not to replace it with the optimized transformation
-- below because the query optimizer can do that. Unfortunately the query
-- optimizer only does this transformation in SELECT contexts and not UPDATE
-- contexts (despite the manual claiming otherwise).
-- CREATE OR REPLACE VIEW clan_highest_scores AS
-- SELECT g.* FROM clan_games AS g
--   LEFT OUTER JOIN clan_games AS g2
--     ON g.team_captain = g2.team_captain AND g.score < g2.score
--   WHERE g2.score IS NULL AND g.score > 0;
CREATE OR REPLACE VIEW clan_highest_scores AS
SELECT p.team_captain,
       JSON_OBJECT('name', teams.name, 'captain', p.team_captain) AS team_info_json,
       g.*,
       JSON_OBJECT('source_file', g.source_file,
                   'player', g.player,
                   'end_time', g.end_time,
                   'charabbrev', g.charabbrev) AS morgue_json
	FROM games AS g
  INNER JOIN players AS p ON g.player = p.name
  LEFT OUTER JOIN (players AS p2 INNER JOIN games AS g2 ON g2.player = p2.name)
    ON p.team_captain = p2.team_captain AND g.score < g2.score
  LEFT JOIN teams
    ON p.team_captain = teams.owner
  WHERE g2.score IS NULL AND g.score > 0 AND p.team_captain IS NOT NULL;

CREATE OR REPLACE VIEW lowest_turncount_wins AS
SELECT g.*, JSON_OBJECT('source_file', g.source_file,
                    'player', g.player,
		    'end_time', g.end_time,
		    'charabbrev', g.charabbrev) AS morgue_json FROM wins AS g
  LEFT OUTER JOIN wins AS g2
  ON g.player = g2.player AND g.turn > g2.turn
  WHERE g2.turn IS NULL;

CREATE OR REPLACE VIEW clan_lowest_turncount_wins AS
SELECT
    JSON_OBJECT('name', teams.name, 'captain', g.team_captain) AS team_info_json,
    g.*,
    JSON_OBJECT('source_file', g.source_file,
                'player', g.player,
                'end_time', g.end_time,
                'charabbrev', g.charabbrev) AS morgue_json
  FROM wins AS g
  LEFT OUTER JOIN wins AS g2
    ON g.team_captain = g2.team_captain AND g.turn > g2.turn
  LEFT JOIN teams
    ON g.team_captain = teams.owner
  WHERE g.team_captain IS NOT NULL AND g2.turn IS NULL;

CREATE OR REPLACE VIEW fastest_wins AS
SELECT g.*, JSON_OBJECT('source_file', g.source_file,
                    'player', g.player,
		    'end_time', g.end_time,
		    'charabbrev', g.charabbrev) AS morgue_json  FROM wins AS g
  LEFT OUTER JOIN wins AS g2
  ON g.player = g2.player AND (g.duration, g.start_time) > (g2.duration, g2.start_time)
  WHERE g2.start_time IS NULL;

CREATE OR REPLACE VIEW clan_fastest_wins AS
SELECT
    JSON_OBJECT('name', teams.name, 'captain', g.team_captain) AS team_info_json,
    g.*,
    JSON_OBJECT('source_file', g.source_file,
                'player', g.player,
                'end_time', g.end_time,
                'charabbrev', g.charabbrev) AS morgue_json
  FROM wins AS g
  LEFT OUTER JOIN wins AS g2
    ON g.team_captain = g2.team_captain AND (g.duration, g.start_time) > (g2.duration, g2.start_time)
  LEFT JOIN teams
    ON g.team_captain = teams.owner
  WHERE g.team_captain IS NOT NULL AND g2.start_time IS NULL;

CREATE OR REPLACE VIEW nonhep_nonfe_wins AS
SELECT * FROM wins AS g
  WHERE NOT EXISTS (SELECT m.id FROM milestones AS m
                        WHERE m.src = g.src AND m.start_time = g.start_time
                        AND (m.verb = 'god.renounce' OR m.verb='god.worship')
                        AND m.noun = 'Hepliaklqana')
	AND NOT g.raceabbr = 'Fe';

CREATE OR REPLACE VIEW low_xl_nonhep_nonfe_wins AS
SELECT g.*, JSON_OBJECT('source_file', g.source_file,
                    'player', g.player,
		    'end_time', g.end_time,
		    'charabbrev', g.charabbrev) AS morgue_json  FROM nonhep_nonfe_wins AS g
  LEFT OUTER JOIN nonhep_nonfe_wins AS g2
  ON g.player = g2.player AND (g.xl, g.start_time) > (g2.xl, g2.start_time)
  WHERE g2.start_time IS NULL AND g.xl < 27;

CREATE OR REPLACE VIEW player_win_perc AS
SELECT player,
  CAST( (SUM(killertype='winning') / (COUNT(*) + 1.0)) * 100.0 AS DECIMAL(5,2)) AS win_perc,
  SUM(killertype = 'winning') as n_wins,
  COUNT(*) as n_games
FROM games GROUP BY player;

-- My kingdom for a full join. Correct handling for Gozag, Xom, and No God
CREATE OR REPLACE VIEW player_god_usage AS
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

CREATE OR REPLACE VIEW player_piety_score AS
SELECT player, JSON_ARRAYAGG(max_piety) AS champion,
	  JSON_ARRAYAGG(won) AS won,
	  COUNT(DISTINCT max_piety) + COUNT(DISTINCT won) AS piety
  FROM player_god_usage
  GROUP BY player;

CREATE OR REPLACE VIEW clan_piety_score AS
SELECT p.team_captain,
    JSON_OBJECT('name', teams.name, 'captain', p.team_captain) AS team_info_json,
    JSON_ARRAYAGG(g.max_piety) AS champion,
    JSON_ARRAYAGG(g.won) AS won,
	  COUNT(DISTINCT g.max_piety) + COUNT(DISTINCT g.won) AS piety
  FROM player_god_usage AS g
    INNER JOIN players AS p ON g.player = p.name
    LEFT JOIN teams ON p.team_captain = teams.owner
  WHERE team_captain IS NOT NULL
  GROUP BY p.team_captain;

CREATE OR REPLACE VIEW player_banner_score AS
SELECT player, SUM(IF(prestige = 3, 4, prestige)) AS bscore,
       JSON_OBJECTAGG(banner, prestige) AS banners
  FROM player_banners WHERE temp = false GROUP BY player;

CREATE OR REPLACE VIEW clan_player_banners AS
SELECT p.team_captain, b.banner, MAX(b.prestige) As prestige
  FROM player_banners AS b INNER JOIN players AS p ON b.player = p.name
 WHERE p.team_captain IS NOT NULL AND b.temp = false
 GROUP BY p.team_captain, b.banner;

CREATE OR REPLACE VIEW clan_banner_score AS
SELECT
    team_captain,
    JSON_OBJECT('name', teams.name, 'captain', team_captain) AS team_info_json,
    SUM( IF(prestige = 3, 4, prestige)) AS bscore,
    JSON_OBJECTAGG(banner, prestige) AS banners
  FROM
    clan_player_banners
    LEFT JOIN teams
      ON team_captain = teams.owner
  GROUP BY
    team_captain;

CREATE OR REPLACE VIEW branch_enter_count AS
SELECT player, COUNT(DISTINCT br) AS score,
       JSON_ARRAYAGG(br) AS data
  FROM branch_enters GROUP BY player;

CREATE OR REPLACE VIEW clan_branch_enter_count AS
SELECT p.team_captain, COUNT(DISTINCT br) AS score,
       JSON_ARRAYAGG(br) AS data
  FROM branch_enters AS b INNER JOIN players AS p ON b.player = p.name
  GROUP BY p.team_captain;

CREATE OR REPLACE VIEW branch_end_count AS
SELECT player, COUNT(DISTINCT br) AS score,
       JSON_ARRAYAGG(br) AS data
  FROM branch_ends GROUP BY player;

CREATE OR REPLACE VIEW clan_branch_end_count AS
SELECT p.team_captain, COUNT(DISTINCT br) AS score,
       JSON_ARRAYAGG(br) AS data
  FROM branch_ends AS b INNER JOIN players AS p ON b.player = p.name
  GROUP BY p.team_captain;

CREATE OR REPLACE VIEW scaled_rune_find_count AS
SELECT player, 3*COUNT(DISTINCT rune) AS score,
       JSON_ARRAYAGG(rune) AS data
  FROM rune_finds GROUP BY player;

CREATE OR REPLACE VIEW clan_scaled_rune_find_count AS
SELECT p.team_captain, 3*COUNT(DISTINCT r.rune) AS score,
       JSON_ARRAYAGG(rune) AS data
  FROM rune_finds AS r INNER JOIN players AS p ON r.player = p.name
  GROUP BY p.team_captain;

CREATE OR REPLACE VIEW exploration_union AS
SELECT player, score AS score, "enters" AS mt, data AS data
  FROM branch_enter_count
UNION ALL SELECT player, score, "ends", data FROM branch_end_count
  UNION ALL SELECT player, score, "runes", data FROM scaled_rune_find_count;

CREATE OR REPLACE VIEW clan_exploration_union AS
SELECT team_captain, score, "enters" AS mt, data
  FROM clan_branch_enter_count
  UNION ALL SELECT team_captain, score, "ends", data FROM clan_branch_end_count
  UNION ALL SELECT team_captain, score, "runes", data FROM clan_scaled_rune_find_count;

-- Can't use a join here because of (starting) abyss shenanigains
-- and there's no full outer join
CREATE OR REPLACE VIEW player_exploration_score AS
SELECT player, SUM(score) AS score, JSON_OBJECTAGG(mt, data) AS data
  FROM exploration_union GROUP BY player;

CREATE OR REPLACE VIEW clan_exploration_score AS
SELECT team_captain,
       JSON_OBJECT('name', teams.name, 'captain', team_captain) AS team_info_json,
       SUM(score) AS score,
       JSON_OBJECTAGG(mt, data) AS data
  FROM clan_exploration_union
    LEFT JOIN teams ON teams.owner = team_captain
  WHERE team_captain IS NOT NULL
  GROUP BY team_captain;

CREATE OR REPLACE VIEW unique_kill_count AS
SELECT player, COUNT(DISTINCT monster) AS score,
       JSON_ARRAYAGG(monster) AS data
  FROM kills_of_uniques GROUP BY player;

CREATE OR REPLACE VIEW clan_unique_kill_count AS
SELECT p.team_captain, COUNT(DISTINCT u.monster) AS score,
       JSON_ARRAYAGG(monster) AS data
  FROM kills_of_uniques AS u INNER JOIN players AS p
    ON u.player = p.name
  GROUP BY p.team_captain;

CREATE OR REPLACE VIEW ghost_kill_count AS
SELECT player, IF(COUNT(*) <= 3, COUNT(*), 3) AS score FROM kills_of_ghosts GROUP BY player;

CREATE OR REPLACE VIEW clan_ghost_kill_count AS
SELECT p.team_captain,  IF(COUNT(*) <= 3, COUNT(*), 3) AS score
  FROM kills_of_ghosts AS u INNER JOIN players AS p
    ON u.player = p.name
  GROUP BY p.team_captain;

CREATE OR REPLACE VIEW harvest_union AS
SELECT player, score, "uniques" AS mt, data FROM unique_kill_count
UNION ALL SELECT player, score, "ghosts", score FROM ghost_kill_count;

CREATE OR REPLACE VIEW clan_harvest_union AS
SELECT team_captain, score, "uniqes" AS mt, data FROM clan_unique_kill_count
UNION ALL SELECT team_captain, score, "ghosts", score FROM clan_ghost_kill_count;

-- Can't use a join because a player could have one but not the other
-- and there's no full outer join
CREATE OR REPLACE VIEW player_harvest_score AS
SELECT player, SUM(score) AS score, JSON_OBJECTAGG(mt, data) AS data
  FROM harvest_union
  GROUP BY player;

CREATE OR REPLACE VIEW clan_harvest_score AS
SELECT team_captain,
       JSON_OBJECT('name', teams.name, 'captain', team_captain) AS team_info_json,
       SUM(score) AS score, JSON_OBJECTAGG(mt, data) AS data
  FROM clan_harvest_union
    LEFT JOIN teams ON team_captain = teams.owner
  WHERE team_captain IS NOT NULL
  GROUP BY team_captain;

CREATE OR REPLACE VIEW player_combo_score AS
SELECT c.player AS player,
       SUM(c.xl >= 9) + 9 * SUM(c.killertype='winning')
                 + 27 * COUNT(sp.raceabbr) + 27 * COUNT(cl.class) AS total,
       SUM(c.xl >= 9) AS combos,
       SUM(c.killertype='winning') AS won_combos,
       COUNT(sp.raceabbr) AS sp_hs, COUNT(cl.class) AS cls_hs,
       JSON_ARRAYAGG(JSON_OBJECT('source_file', c.source_file,
                    'player', c.player,
		    'end_time', c.end_time,
		    'charabbrev', c.charabbrev,
	            'won', c.killertype='winning',
	            'sp_hs', sp.raceabbr,
	            'cls_hs', MID(cl.charabbrev,3,2))) AS games_json
  FROM combo_highscores AS c
  LEFT OUTER JOIN species_highscores AS sp
    ON c.player = sp.player AND c.charabbrev = sp.charabbrev
  LEFT OUTER JOIN class_highscores AS cl
    ON c.player = cl.player AND c.charabbrev = cl.charabbrev
  GROUP BY c.player;

CREATE OR REPLACE VIEW clan_combo_score AS
SELECT p.team_captain,
       JSON_OBJECT('name', teams.name, 'captain', team_captain) AS team_info_json,
       SUM(c.xl >= 9) + 9 * SUM(c.killertype='winning')
                 + 27 * COUNT(sp.raceabbr) + 27 * COUNT(cl.class) AS total,
       SUM(c.xl >= 9) AS combos,
       COUNT(c.killertype='winning') AS won_combos,
       COUNT(sp.raceabbr) AS sp_hs, COUNT(cl.class) AS cls_hs,
       JSON_ARRAYAGG(JSON_OBJECT('source_file', c.source_file,
                    'player', c.player,
		    'end_time', c.end_time,
		    'charabbrev', c.charabbrev,
	            'won', c.killertype='winning',
	            'sp_hs', sp.raceabbr,
	            'cls_hs', MID(cl.charabbrev,3,2))) AS games_json
  FROM combo_highscores AS c
  LEFT OUTER JOIN species_highscores AS sp
    ON c.player = sp.player AND c.charabbrev = sp.charabbrev
  LEFT OUTER JOIN class_highscores AS cl
    ON c.player = cl.player AND c.charabbrev = cl.charabbrev
  INNER JOIN players AS p
    ON c.player = p.name
  LEFT JOIN teams
    ON team_captain = teams.owner
  WHERE p.team_captain IS NOT NULL
  GROUP BY p.team_captain;

CREATE OR REPLACE VIEW player_nem_scored_wins AS
SELECT IF(ROW_NUMBER() OVER (PARTITION BY charabbrev ORDER BY end_time) < 10,
	1, 0) AS nem_counts, n.player, n.charabbrev,
	JSON_OBJECT('source_file', n.source_file,
                    'player', n.player,
		    'end_time', n.end_time,
		    'charabbrev', n.charabbrev) AS xdict
  FROM player_nemelex_wins AS n;

CREATE OR REPLACE VIEW player_nemelex_score AS
SELECT player, COUNT(DISTINCT charabbrev) AS score,
       JSON_ARRAYAGG(xdict) AS games
FROM player_nem_scored_wins
WHERE nem_counts = 1
GROUP BY player;

-- This is a view because clan affiliation can change and we don't want
-- to re-insert the table after time goes by
CREATE OR REPLACE VIEW clan_nemelex_wins AS
SELECT p.team_captain,
       ROW_NUMBER() OVER (PARTITION BY p.team_captain, n.charabbrev
	                  ORDER BY end_time) AS clan_finish, n.*
  FROM player_nemelex_wins AS n INNER JOIN players AS p ON n.player = p.name
  WHERE p.team_captain IS NOT NULL;

CREATE OR REPLACE VIEW clan_nem_scored_wins AS
SELECT IF(ROW_NUMBER() OVER (PARTITION BY charabbrev ORDER BY end_time) < 10,
	  1, 0) AS nem_counts, n.team_captain, n.charabbrev,
	JSON_OBJECT('source_file', source_file,
                    'player', player,
		    'end_time', end_time,
		    'charabbrev', charabbrev) AS xdict
  FROM clan_nemelex_wins AS n WHERE n.clan_finish = 1;

CREATE OR REPLACE VIEW clan_nemelex_score AS
  SELECT team_captain,
         JSON_OBJECT('name', teams.name, 'captain', team_captain) AS team_info_json,
         COUNT(DISTINCT charabbrev) AS score,
         JSON_ARRAYAGG(xdict) AS games
  FROM clan_nem_scored_wins
    LEFT JOIN teams ON team_captain = teams.owner
  WHERE nem_counts = 1 AND team_captain IS NOT NULL
  GROUP BY team_captain;

CREATE OR REPLACE VIEW player_best_streak AS
SELECT DISTINCT s.player, s.length, s.streak_data FROM streaks AS s
  LEFT OUTER JOIN streaks AS s2
    ON s.player = s2.player AND (s.length, s.start_time) < (s2.length, s2.start_time)
  WHERE s2.start_time IS NULL;

CREATE OR REPLACE VIEW clan_streaks AS
SELECT p.team_captain, s.player, s.length
FROM streaks AS s INNER JOIN players AS p ON s.player = p.name
WHERE p.team_captain IS NOT NULL;

CREATE OR REPLACE VIEW clan_best_streak AS
SELECT
  s.team_captain,
  JSON_OBJECT('name', teams.name, 'captain', s.team_captain) AS team_info_json,
  GROUP_CONCAT(DISTINCT s.player) AS players,
  s.length
FROM clan_streaks AS s
  LEFT OUTER JOIN clan_streaks AS s2
    ON s.team_captain = s2.team_captain AND s.length < s2.length
  LEFT JOIN teams
    ON s.team_captain = teams.owner
  WHERE s2.length IS NULL AND s.team_captain IS NOT NULL
GROUP BY s.team_captain, s.length;

CREATE OR REPLACE VIEW player_ziggurats AS
SELECT z.player, 28 * z.completed + z.deepest AS floors, z.completed, z.deepest
  FROM ziggurats AS z;

CREATE OR REPLACE VIEW clan_ziggurats AS
SELECT p.team_captain, z.player, 28 * z.completed + z.deepest AS floors,
       z.completed, z.deepest
  FROM ziggurats AS z INNER JOIN players AS p ON p.name = z.player
  WHERE p.team_captain IS NOT NULL;

CREATE OR REPLACE VIEW clan_best_ziggurat AS
SELECT z.team_captain,
       JSON_OBJECT('name', teams.name, 'captain', z.team_captain) AS team_info_json,
       GROUP_CONCAT(DISTINCT z.player) AS players,
       z.floors,
       z.completed,
       z.deepest
  FROM clan_ziggurats AS z
  LEFT OUTER JOIN clan_ziggurats AS z2
    ON z.team_captain = z2.team_captain
       AND (z.completed, z.deepest) < (z2.completed, z2.deepest)
  LEFT JOIN teams
    ON z.team_captain = teams.owner
  WHERE z2.deepest IS NULL
GROUP BY z.team_captain, z.completed, z.deepest;

CREATE OR REPLACE VIEW clan_combo_first_wins AS
SELECT g.*,
  IF(ROW_NUMBER() OVER (PARTITION BY g.player ORDER BY g.end_time) <= 4, 1, 0)
    AS first_four
  FROM wins AS g
  LEFT OUTER JOIN wins AS g2
    ON g.team_captain = g2.team_captain AND g.charabbrev = g2.charabbrev
       AND g.end_time > g2.end_time
  WHERE g2.end_time IS NULL AND g.team_captain IS NOT NULL;
