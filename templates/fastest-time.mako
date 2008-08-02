<%
   import loaddb, query, html
   c = attributes['cursor']

   game_text = \
      html.games_table( query.get_fastest_time_player_games(c),
                        first = 'duration' )
%>

${game_text}
