<%
   import loaddb, query, htmlgen
   c = attributes['cursor']

   text = htmlgen.table_text( [ 'Player', 'Uniques Slain', 'Time' ],
                           query.get_top_unique_killers(c) )
%>

${text}
