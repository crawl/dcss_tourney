<%
   import loaddb, query, htmlgen
   c = attributes['cursor']

   game_text = \
      htmlgen.games_table( query.find_games(c, killertype='winning', limit=3),
                        first = 'end_time' )
%>

${game_text}
