<%
   import loaddb, query, htmlgen
   c = attributes['cursor']

   text = htmlgen.table_text( [ 'Player', 'Win Percentage' ],
   							query.win_perc_order(c), place_column=1, skip=True)
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Streak Ranking</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

         <h2>Active Streaks</h2>
          ${htmlgen.best_active_streaks(c)}

        <h2>Streak Ranking</h2>
        <div class="fineprint">
		  XXX: Streak rules.
        </div>

		${htmlgen.best_streaks(c)}
	  </div>

    ${htmlgen.update_time()}
  </body>
</html>
