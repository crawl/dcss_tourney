<%
   import loaddb, query, htmlgen
   c = attributes['cursor']

   game_text = \
      htmlgen.games_table( query.get_fastest_turn_player_games(c),
                        first = 'turn' )
%>

${game_text}
