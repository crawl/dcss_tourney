<%
   import loaddb, query, html
   c = attributes['cursor']

   game_text = \
      html.games_table( [ ('player', 'Player'),
                          ('turn', 'Turns'),
                          ('duration', 'Duration'),
                          ('score', 'Score', True),
                          ('charabbrev', 'Character'),
                          ('god', 'God'),
                          ('end_time', 'Time', True)
                          ],
                        query.find_games(c, killertype='winning',
                                         sort_min = 'turn',
                                         limit=3) )
%>

${game_text}
