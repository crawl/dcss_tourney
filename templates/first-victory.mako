<%
   import loaddb, query, html
   c = attributes['cursor']

   game_text = \
      html.games_table( [ ('player', 'Player'),
                          ('end_time', 'Time', True),
                          ('score', 'Score', True),
                          ('charabbrev', 'Character'),
                          ('god', 'God'),
                          ('turn', 'Turns') ],
                        query.find_games(c, killertype='winning', limit=3) )
%>

${game_text}
