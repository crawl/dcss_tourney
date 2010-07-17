<%

   import loaddb, query, crawl_utils, html, combos
   c = attributes['cursor']

   won, unwon = query.won_unwon_combos(c)
   won_sprint, unwon_sprint = query.sprint_won_unwon_combos(c)
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

        % if won:
        <h2>Won Combos</h2>
        <div class="fineprint">
          Species-class combinations won during the tournament.
        </div>
        <div class="inset">
          ${", ".join(won)}
        </div>
        <hr>
        %endif

        <h2>Unwon Combos</h2>

        <div class="fineprint">
          Species-class combinations unwon during the tournament.
        </div>

        <div class="inset">
          % if unwon:
          ${", ".join(unwon)}
          % else:
          <b>All combos have been won (?!)</b>
          % endif
        </div>

        <hr>

        % if won_sprint:
        <h2>Won Sprint Combos</h2>
        <div class="fineprint">
          Species-class combinations won in Sprint during the tournament.
        </div>
        <div class="inset">
          ${", ".join(won_sprint)}
        </div>
        <hr>
        %endif

        <h2>Unwon Sprint Combos</h2>

        <div class="fineprint">
          Species-class combinations unwon in Sprint during the tournament.
        </div>

        <div class="inset">
          % if unwon_sprint:
          ${", ".join(unwon_sprint)}
          % else:
          <b>All Sprint combos have been won (?!)</b>
          % endif
        </div>
      </div>
    </div>
  </body>
</html>
