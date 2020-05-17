<%
   import loaddb, query, html
   c = attributes['cursor']

   text = html.table_text( [ 'Player', 'Gods Championed', 'Gods Won', 'Piety Score' ],
   							query.piety_order(c), place_column=3, skip=True)
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Piety Ranking</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Piety Ranking</h2>
        <div class="fineprint">
		  Players earn one point for becoming the champion (****** piety) and
		  an additional point for a win after chapioning that god. Two gods
		  (Gozag and Xom) do not have the usual ****** piety system; to get the
		  points for these gods, you must never worship another god during the
		  game.
        </div>

		${text}
	  </div>

    ${html.update_time()}
  </body>
</html>
