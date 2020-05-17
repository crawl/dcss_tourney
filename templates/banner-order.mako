<%
   import loaddb, query, html
   c = attributes['cursor']

   text = html.table_text( [ 'Player', 'Banner Score', 'Banners Earned' ],
   							query.banner_order(c), place_column=1, skip=True)
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Banner Score Ranking</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Banner Score Ranking</h2>
        <div class="fineprint">
		  Each god awards a banner with three tiers, banner tiers award 1, 2,
		  or 4 points in this category.
        </div>

		${text}
	  </div>

    ${html.update_time()}
  </body>
</html>
