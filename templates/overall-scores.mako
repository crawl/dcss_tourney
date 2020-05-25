<%
   import loaddb, query, htmlgen
   c = attributes['cursor']

   text = htmlgen.table_text( [ 'Player', 'Points' ],
                           query.get_top_players(c),
                           place_column=1, skip=True )
%>

${text}
