<%

   import loaddb, query, crawl_utils, html, combos
   c = attributes['cursor']

   all_nemelex_wins = query.get_nemelex_wins(c)

   players = { }

   for game in all_nemelex_wins:
     name = query.canonicalize_player_name(c, game['player'])
     players[name] = (players.get(name) or [])
     players[name].append(game)

   linkified_combo_list = \
       {  p : ", ".join([ crawl_utils.linked_text(
                             g, crawl_utils.morgue_link, g['charabbrev'])
                          for g in gms ]) for p,gms in players.items() }
   nemelex_order = query.nemelex_order(c)
   data = [ [query.canonicalize_player_name(c, r[0]), r[1],
             linkified_combo_list[query.canonicalize_player_name(c, r[0])] ]
             for r in nemelex_order ]

   text = html.table_text( [ 'Player', "Nemelex' Choice Wins", 'Combos' ],
                           data, place_column=1, skip=True )

%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Nemelex' Choice Rank</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">

        <h2>Nemelex' Choice Rank</h2>
        <div class="fineprint">
		  XXX: Describe this.
        </div>

        ${text}

      </div>
    </div>

    ${html.update_time()}
  </body>
</html>
