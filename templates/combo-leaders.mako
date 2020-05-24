<%inherit file="base.mako"/>

<%!
  import scoring_data
  import html
  import query
  import crawl_utils

  active_menu_item = None
%>

<%block name="title">
  Combo High Scores Ranking
</%block>

<%block name="main">
  <%
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
  %>
  <div class="row">
    <div class="col">
      <h2>Individual Combo High Scores Rank</h2>
      <p>
        Players with the highest combo-high-scores points. Players earn one
        point for each species-background combo high-score, an additional
        point for a combo high-score that is a winning game, and three
        additional points for species and background high-scores.
      </p>

      ${html.table_text( [ 'Player', 'Combo High Scores Points', 'Combos' ],
                            data, place_column=1, skip=True )}
    </div>
  </div>
</%block>
