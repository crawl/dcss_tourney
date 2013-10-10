<%

   import loaddb, query, crawl_utils, html, combos
   c = attributes['cursor']

   all_combo_scores = query.get_combo_scores(c)

   text = html.ext_games_table(all_combo_scores,
                               excluding=['race', 'class'],
                               including=[(1, ('charabbrev', 'Combo'))])
   count = len(all_combo_scores)

   played = set( [ g['charabbrev'] for g in all_combo_scores ] )

   unplayed = [ c for c in combos.VALID_COMBOS if c not in played ]
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Combo Scoreboard</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Combo Scoreboard</h2>
        <div class="fineprint">
          Highest scoring game for each species-background combination played
          in the tournament.
        </div>

        ${text}

        <div class="inset">
          <div>
          % if unplayed:
          <b>${len(unplayed)} combos have not been played:</b>
          % else:
          <b>All combos have been played at least once.</b>
          % endif
          </div>
          ${", ".join(unplayed)}
        </div>
      </div>
    </div>

    ${html.update_time()}
  </body>
</html>
