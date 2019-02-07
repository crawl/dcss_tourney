<%
   import loaddb, query, crawl_utils, html

   c = attributes['cursor']

   stats = query.get_all_player_stats(c, max_games=10)
 %>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>10 game challenge</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>


  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">
        <div class="heading_left">
          <h1>10 game challenge</h1>
        </div>

        <hr>

        <div class="page_content">How well can you do, playing 10 games or fewer during the tournament?</div>

        <div class="content">
          ${html.table_text( [ 'Player', 'Clan', 'Points',
                               'Games Won', 'Games Played',
                               'Win %' ],
                             stats,
                             place_column=2, skip=True )}
        </div>
      </div>
    </div>
    ${html.update_time()}
  </body>
</html>
