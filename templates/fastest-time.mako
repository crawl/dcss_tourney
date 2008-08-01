<%
   import loaddb, query, html
   c = attributes['cursor']

   game_text = \
      html.games_table( [ ('player', 'Player'),
                          ('duration', 'Duration'),
                          ('turn', 'Turns'),
                          ('score', 'Score', True),
                          ('charabbrev', 'Character'),
                          ('god', 'God'),
                          ('end_time', 'Time', True),
                          ],
                        query.find_games(c, killertype='winning',
                                         sort_min = 'duration',
                                         limit=3) )
%>

${game_text}
