<%
   import loaddb, query, html
   c = attributes['cursor']

   text = html.table_text( [ 'Player', 'Points' ],
                           query.get_top_players(c) )
%>

${text}
