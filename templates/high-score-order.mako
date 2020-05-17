<%
   import loaddb, query, html
   c = attributes['cursor']

   game_text = \
      html.games_table( query.high_score_order(c, limit = None),
                        first = 'score', place_column = 1 )
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Best High Score Ranking</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Best High Score Ranking</h2>

		${game_text}
	  </div>

    ${html.update_time()}
  </body>
</html>
