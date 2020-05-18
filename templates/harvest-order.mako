<%
   import loaddb, query, html
   c = attributes['cursor']

   text = html.table_text( [ 'Player', 'Harvest Score' ],
   							query.harvest_order(c), place_column=1, skip=True)
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Harvest Ranking</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Harvest Ranking</h2>
        <div class="fineprint">
		   In this category, players earn 1 point for each distinct unique
		   killed and 1 point for each player ghost killed.
		</div>

		${text}
	  </div>

    ${html.update_time()}
  </body>
</html>
