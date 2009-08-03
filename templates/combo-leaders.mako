<%

   import loaddb, query, crawl_utils, html, combos
   c = attributes['cursor']

   all_combo_scores = query.get_combo_scores(c)

   players = { }

   for game in all_combo_scores:
     name = game['player']
     players[name] = (players.get(name) or [])
     players[name].append(game)

   players = players.items()
   players.sort(lambda a,b: len(b[1]) - len(a[1]))

   data = [ [ p[0], len(p[1]),
              ", ".join([ crawl_utils.linked_text(
                             g, crawl_utils.morgue_link, g['charabbrev'])
                          for g in p[1] ]) ]
            for p in players ]

   text = html.table_text( [ 'Player', 'Count', 'Combos' ],
                           data )
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Combo Standings</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Combo Standings</h2>
        <div class="fineprint">
          Players with the most species-class combination high-scores.
        </div>

        ${text}

      </div>
    </div>

    ${html.update_time()}
  </body>
</html>
