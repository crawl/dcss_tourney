<%
   import loaddb, query, html
   c = attributes['cursor']

   game_text = \
      html.games_table( query.get_fastest_turn_player_games(c),
                        first = 'turn' )
%>

${game_text}
