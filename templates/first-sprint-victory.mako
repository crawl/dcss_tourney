<%
   import loaddb, query, html
   c = attributes['cursor']

   game_text = \
      html.games_table(
        query.sprint_find_first_victories(c, limit=3),
        first = 'end_time' )
%>

${game_text}
