<%

   import loaddb, query, crawl_utils, html, combos
   c = attributes['cursor']

   all_combo_scores = query.get_combo_scores(c)

   players = { }

   for game in all_combo_scores:
     name = query.canonicalize_player_name(c, game['player'])
     players[name] = (players.get(name) or [])
     players[name].append(game)

   linkified_combo_list = \
       {  p : ", ".join([ crawl_utils.linked_text(
                             g, crawl_utils.morgue_link, g['charabbrev'])
                          for g in gms ]) for p,gms in players.items() }
   combo_score_order = query.combo_score_order(c)
   data = [ [query.canonicalize_player_name(c, r[0]), r[1],
             linkified_combo_list[query.canonicalize_player_name(c, r[0])] ]
             for r in combo_score_order ]

   text = html.table_text( [ 'Player', 'Combo High-Scores Points', 'Combos' ],
                           data, place_column=1, skip=True )
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Combo High Scores Rank</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Individual Combo High Scores Rank</h2>
        <div class="fineprint">
		  Players with the highest combo-high-scores points. Players earn one
		  point for each species-background combo high-score, an additional
		  point for a combo high-score that is a winning game, and three
		  additional points for species and background high-scores.
        </div>

        ${text}

      </div>
    </div>

    ${html.update_time()}
  </body>
</html>
