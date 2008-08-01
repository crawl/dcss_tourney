<%
   import loaddb, query, html
   c = attributes['cursor']

   game_text = \
      html.games_table( query.find_games(c, killertype='winning', limit=3),
                        first = 'end_time' )
%>

${game_text}
