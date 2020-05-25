<%
   import loaddb, query, crawl_utils, htmlgen, re
   c = attributes['cursor']

   death_causes = query.get_death_causes(c)

   r_ghost = re.compile(r'^player ghost')
   for c in death_causes:
     if c[0].startswith('player ghost'):
       c[0] = r_ghost.sub('<a href="gkills.html">player ghost</a>', c[0])

   table = htmlgen.table_text([ 'Killer', '%', 'Kills', 'Last Victim' ],
                           death_causes, place_column=2, skip=True)

%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Killers</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page_narrow">
      <%include file="toplink.mako"/>

      <div class="page_content">
        <div class="heading">
          <h2>Top Killers</h2>
        </div>
        ${table}
      </div>
    </div>

    ${htmlgen.update_time()}
  </body>
</html>
