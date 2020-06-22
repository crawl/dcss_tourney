DROP VIEW fastest_wins;

CREATE VIEW fastest_wins AS
SELECT g.*, JSON_OBJECT('source_file', g.source_file,
                    'player', g.player,
		    'end_time', g.end_time,
		    'charabbrev', g.charabbrev) AS morgue_json  FROM wins AS g
  LEFT OUTER JOIN wins AS g2
  ON g.player = g2.player AND (g.duration, g.start_time) > (g2.duration, g2.start_time)
  WHERE g2.start_time IS NULL
  GROUP BY g.player;

DROP VIEW clan_fastest_wins;

CREATE VIEW clan_fastest_wins AS
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

DROP VIEW low_xl_nonhep_wins;

CREATE VIEW low_xl_nonhep_wins AS
SELECT g.*, JSON_OBJECT('source_file', g.source_file,
                    'player', g.player,
		    'end_time', g.end_time,
		    'charabbrev', g.charabbrev) AS morgue_json  FROM nonhep_wins AS g
  LEFT OUTER JOIN nonhep_wins AS g2
  ON g.player = g2.player AND (g.xl, g.start_time) > (g2.xl, g2.start_time)
  WHERE g2.start_time IS NULL AND g.xl < 27;

DROP VIEW player_best_streak;

CREATE VIEW player_best_streak AS
SELECT DISTINCT s.player, s.length, s.streak_data FROM streaks AS s
  LEFT OUTER JOIN streaks AS s2
    ON s.player = s2.player AND (s.length, s.start_time) < (s2.length, s2.start_time)
  WHERE s2.start_time IS NULL;
