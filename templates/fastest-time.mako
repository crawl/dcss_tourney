<%
   import loaddb, query, htmlgen
   c = attributes['cursor']

   game_text = \
      htmlgen.games_table( query.get_fastest_time_player_games(c),
                        first = 'duration' )
%>

${game_text}
