<%

   import loaddb, query, crawl_utils, html, combos, crawl
   c = attributes['cursor']

   all_species = set([ comb[:2] for comb in combos.VALID_COMBOS])
   all_classes = set([ comb[2:4] for comb in combos.VALID_COMBOS])
   all_gods = set(crawl.GODS)
   num_wins = query.count_wins(c)

   species_data = [ [ r, query.count_wins(c, raceabbr=r) ]
            for r in all_species ]
   species_data.sort(key=lambda e: e[0])
   species_data.sort(key=lambda e: e[1])

   class_data = [ [ r, query.count_wins(c, classabbr=r) ]
            for r in all_classes ]
   class_data.sort(key=lambda e: e[0])
   class_data.sort(key=lambda e: e[1])

   god_data = [ [ r, query.count_god_wins(c, r) ]
            for r in all_gods ]
   god_data.sort(key=lambda e: e[0])
   god_data.sort(key=lambda e: e[1])

   condensed_species_data = []
   last_count = -1
   point_value = -1
   for s in species_data:
     if s[1] == last_count:
       species_list = "%s, %s" % (species_list, s[0])
     else:
       if last_count > -1:
         condensed_species_data = condensed_species_data + [[last_count, species_list, point_value],]
       species_list = s[0]
       last_count = s[1]
       point_value = query.race_formula(num_wins, last_count)
   condensed_species_data = condensed_species_data + [[last_count, species_list, point_value],]

   condensed_class_data = []
   last_count = -1
   point_value = -1
   for s in class_data:
     if s[1] == last_count:
       class_list = "%s, %s" % (class_list, s[0])
     else:
       if last_count > -1:
         condensed_class_data = condensed_class_data + [[last_count, class_list, point_value],]
       class_list = s[0]
       last_count = s[1]
       point_value = query.class_formula(num_wins, last_count)
   condensed_class_data = condensed_class_data + [[last_count, class_list, point_value],]

   condensed_god_data = []
   last_count = -1
   point_value = -1
   for s in god_data:
     if s[1] == last_count:
       god_list = "%s, %s" % (god_list, s[0])
     else:
       if last_count > -1:
         condensed_god_data = condensed_god_data + [[last_count, god_list, point_value],]
       god_list = s[0]
       last_count = s[1]
       point_value = query.god_formula(num_wins, last_count)
   condensed_god_data = condensed_god_data + [[last_count, god_list, point_value],]

   species_text = html.table_text( [ 'Wins', 'Species', 'Current Value'],
                           condensed_species_data, count=False)
   class_text = html.table_text( [ 'Wins', 'Background', 'Current Value'],
                           condensed_class_data, count=False)
   god_text = html.table_text( [ 'Wins', 'God', 'Current Value'],
                           condensed_god_data, count=False)

   all_species_scores = query.get_species_scores(c)
   all_class_scores = query.get_class_scores(c)
   species_scores_text = html.ext_games_table(all_species_scores,
                                              excluding=['class'],
                                              including=[(2, ('charabbrev', 'Combo'))])
   class_scores_text = html.ext_games_table(all_class_scores,
                                            excluding=['race'],
                                            including=[(2, ('charabbrev', 'Combo'))])


%>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Species/Backgrounds/Gods</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">
        <h2>Wins by Species</h2>
        ${species_text}
	<h2>Wins by Background</h2>
        ${class_text}
	<h2>Wins by God</h2>
            <p class="fineprint">
              We say that a game is won using a (non-Gozag, non-Xom) god if the player reaches
              ****** piety with that god without worshipping any
              other god first; this is not necessarily the same god worshipped at the end of the game. A game is won using Gozag or Xom if the player never worships another god. A game is won using 'No God' only if the player
              never worships a god.
            </p>
        ${god_text}
        <hr>

        <h2>Species Scoreboard</h2>
        <div class="fineprint">
          Highest scoring game for each species played
          in the tournament.
        </div>

        ${species_scores_text}

        <h2>Background Scoreboard</h2>
        <div class="fineprint">
          Highest scoring game for each background played
          in the tournament.
        </div>

        ${class_scores_text}

      </div>
    </div>

    ${html.update_time()}
  </body>
</html>
