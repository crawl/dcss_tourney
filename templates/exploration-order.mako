<%
   import loaddb, query, html
   c = attributes['cursor']

   text = html.table_text( [ 'Player', 'Exploration Score' ],
   							query.exploration_order(c), place_column=1, skip=True)
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Exploration Ranking</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Exploration Ranking</h2>
        <div class="fineprint">
		   In this category, players earn 3 points per distinct rune of Zot
		   collected and 1 point each for distinct branch or branch end entered.
        </div>

		${text}
	  </div>

    ${html.update_time()}
  </body>
</html>
