<%
   import loaddb, query, html
   c = attributes['cursor']

   YOUNG_COLUMNS = \
     [ ('player', 'Player'),
       ('xl', 'XL'),
       ('charabbrev', 'Character'),
       ('turn', 'Turns'),
       ('duration', 'Duration'),
       ('god', 'God'),
       ('end_time', 'Time', True)
     ]

   game_text = \
      html.games_table(query.low_xl_win_order(c), columns=YOUNG_COLUMNS,
                        place_column=1)
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Lowest XL Win Ranking</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Lowest XL Win Ranking</h2>
        <div class="fineprint">
		  Players in order of their lowest XL win. Players who have only won at
		  XL 27 do not appear in this ranking.
        </div>

		${game_text}
	  </div>

    ${html.update_time()}
  </body>
</html>
