<%

   import loaddb, query, crawl_utils, html, combos
   c = attributes['cursor']

   all_combo_scores = query.get_combo_scores(c)

   players = { }

   for game in all_combo_scores:
     name = query.canonicalize_player_name(c, game['player'])
     players[name] = (players.get(name) or [])
     players[name].append(game)

   players = players.items()
   players.sort(lambda a,b: len(b[1]) - len(a[1]))

   data = [ [ p[0], len(p[1]),
              ", ".join([ crawl_utils.linked_text(
                             g, crawl_utils.morgue_link, g['charabbrev'])
                          for g in p[1] ]) ]
            for p in players ]

   if len(data) > 20:
     data_truncated = [d for d in data if d[1] >= data[19][1]]
   else:
     data_truncated = data

   text = html.table_text( [ 'Player', 'Count', 'Combos' ],
                           data_truncated, place_column=1, skip=True )

   all_clan_combo_scores = query.get_clan_combo_scores(c)

   clans = { }

   for game in all_clan_combo_scores:
     name = game[0]
     clans[name] = (clans.get(name) or [])
     clans[name].append(game[1])

   clans = clans.items()
   clans.sort(lambda a,b: len(b[1]) - len(a[1]))

   clan_data = [ [ html.linked_text(p[0], crawl_utils.clan_link, query.team_exists(c,p[0])),
              len(p[1]),
              ", ".join([ crawl_utils.linked_text(
                             g, crawl_utils.morgue_link, g['charabbrev'])
                          for g in p[1] ]) ]
            for p in clans ]

   if len(clan_data) > 10:
     clan_data_truncated = [d for d in clan_data if d[1] >= clan_data[9][1]]
   else:
     clan_data_truncated = clan_data

   clan_text = html.table_text( [ 'Clan', 'Count', 'Combos' ],
                           clan_data_truncated, place_column=1, skip=True )
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

        <h2>Clan Combo Standings</h2>
        <div class="fineprint">
          Clans with the most species-class combination high-scores.
        </div>

        ${clan_text}

        <h2>Individual Combo Standings</h2>
        <div class="fineprint">
          Players with the most species-class combination high-scores.
        </div>

        ${text}

      </div>
    </div>

    ${html.update_time()}
  </body>
</html>
