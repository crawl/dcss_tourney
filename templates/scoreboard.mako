<%

   import loaddb, query, crawl_utils, html
   c = attributes['cursor']

   fastest_turns = query.find_games(c, killertype='winning',
                                    sort_min='turn', limit=15)
   fastest_time = query.find_games(c, sort_min='duration',
                                   killertype='winning', limit=15)
   fastest_allrune_time = query.find_games(c, sort_min='duration',
                                   killertype='winning', runes=15, limit=5)
   top_scores = query.find_games(c, sort_max='score', limit=15)

%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Scoreboard</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">
        <div class="content">

        <div class="sidebar">
          <div>
            <h4>Miscellaneous Statistics</h4>
          </div>
          <div class="sidebar_content">
            <p>
              <a href="killers.html">Top Killers</a>
            </p>
            <p>
              <a href="gkills.html">Ghost Kills</a>
            </p>
          </div>
        </div>

        <%include file="games-overview.mako"/>

        <hr style="width: 50%; margin-left: 0px;">

        <div>
          <h2>Fastest Wins (turncount)</h2>
          ${html.ext_games_table(fastest_turns)}
        </div>

        <hr>
        
        <div>
          <h2>Fastest Wins (real time)</h2>
          ${html.ext_games_table(fastest_time)}
        </div>

        <hr>

        <div>
          <h2>Top Scores</h1>

          ${html.ext_games_table(top_scores)}
        </div>

	<hr>

	<div>
          <h2>Fastest 15-Rune Wins (real time)</h2>
          ${html.ext_games_table(fastest_allrune_time)}
        </div>

        </div>
      </div>
    </div>

    ${html.update_time()}
  </body>
</html>
