<%
   import loaddb, query, crawl_utils, html

   c = attributes['cursor']

   stats = query.get_all_player_stats(c)
 %>

<html>
  <head>
    <title>All Players</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>


  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>
      <div class="heading_left">
        <h1>All Players</h1>
      </div>

      <hr/>

      <div class="content">
        ${html.table_text( [ 'Player', 'Points', 'Games Won', 'Games Played',
                             'Win %' ],
                           stats )}
      </div>
    </div>
    ${html.update_time()}
  </body>
</html>
