<%

   import loaddb, query, crawl_utils, html, combos
   c = attributes['cursor']

   all_species = set([ comb[:2] for comb in combos.VALID_COMBOS])
   all_classes = set([ comb[2:4] for comb in combos.VALID_COMBOS])

   species_data = [ [ r, query.count_race_wins(c, r) ]
            for r in all_species ]
   species_data.sort(key=lambda e: e[0])
   species_data.sort(key=lambda e: -e[1])

   class_data = [ [ r, query.count_class_wins(c, r) ]
            for r in all_classes ]
   class_data.sort(key=lambda e: e[0])
   class_data.sort(key=lambda e: -e[1])

   condensed_species_data = []
   last_count = -1
   for s in species_data:
     if s[1] == last_count:
       species_list = "%s, %s" % (species_list, s[0])
     else:
       if last_count > -1:
         condensed_species_data = condensed_species_data + [[last_count, species_list],]
       species_list = s[0]
       last_count = s[1]
   condensed_species_data = condensed_species_data + [[last_count, species_list],]

   condensed_class_data = []
   last_count = -1
   for s in class_data:
     if s[1] == last_count:
       class_list = "%s, %s" % (class_list, s[0])
     else:
       if last_count > -1:
         condensed_class_data = condensed_class_data + [[last_count, class_list],]
       class_list = s[0]
       last_count = s[1]
   condensed_class_data = condensed_class_data + [[last_count, class_list],]


   species_text = html.table_text( [ 'Winners', 'Species'],
                           condensed_species_data, count=False)
   class_text = html.table_text( [ 'Winners', 'Class'],
                           condensed_class_data, count=False)




   won, unwon = query.won_unwon_combos(c)
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
        <h2>Species Winners</h2>
        ${species_text}
	<h2>Class Winners</h2>
        ${class_text}
        <hr>

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
      </div>
    </div>
  </body>
</html>
