<%inherit file="base.mako"/>

<%!
   import loaddb, query, crawl_utils, combos
   import tourney_html as html
   active_menu_item = "Combo Scoreboard"
%>

<%block name="title">
  Combo Scoreboard
</%block>

<%block name="main">

  <%
   all_combo_scores = query.get_combo_scores(attributes['cursor'])

   text = html.ext_games_table(all_combo_scores,
                               excluding=['race', 'class'],
                               including=[(1, ('charabbrev', 'Combo'))])
   count = len(all_combo_scores)

   all_species_scores = query.get_species_scores(attributes['cursor'])
   all_class_scores = query.get_class_scores(attributes['cursor'])
   species_scores_text = html.ext_games_table(all_species_scores,
                                              excluding=['class'],
                                              including=[(2, ('charabbrev', 'Co mbo'))])
   class_scores_text = html.ext_games_table(all_class_scores,
                                            excluding=['race'],
                                            including=[(2, ('charabbrev', 'Comb o'))])

   played = set( [ g['charabbrev'] for g in all_combo_scores ] )

   unplayed = [ c for c in combos.VALID_COMBOS if c not in played ]
  %>

  <div class="row">
    <div class="col">
    <h2>Species Scoreboard</h2>
      <p class="lead">
        Highest scoring game for each species played in the tournament.
      </p>
    ${species_scores_text}
    </div>
    <div class="col">
    <h2>Background Scoreboard</h2>
      <p class="lead">
        Highest scoring game for each background played in the tournament.
      </p>
      ${class_scores_text}
    </div>
  </div>
      
  <div class="row">
    <div class="col">
      <h2>Combo Scoreboard</h2>
      <p class="lead">
        Highest scoring game for each species-background combination played
        in the tournament.
      </p>

      ${text}
    </div>
  </div>

  <div class="row">
    <div class="col">
      % if unplayed:
      <h2>${len(unplayed)} combos have not been played:</h2>
      % else:
      <h2>All combos have been played at least once.</h2>
      % endif
      <p class="lead">
        ${", ".join(unplayed)}
      </p>
    </div>
  </div>

</%block>
