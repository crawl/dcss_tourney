<%
   import loaddb, query, htmlgen
   c = attributes['cursor']

   game_text = \
      htmlgen.games_table( query.find_games(c, killertype='winning',
                                         runes = query.MAX_RUNES,
                                         limit=3) )
%>

${game_text}
