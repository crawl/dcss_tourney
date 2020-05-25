<%inherit file="base.mako"/>

<%!
  import htmlgen
  import query
  import crawl_utils

  active_menu_item = None
%>

<%block name="title">
  Nemelex' Choice Rank
</%block>

<%block name="main">
  <%
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
  %>
  <div class="row">
    <div class="col">
      <h2>Nemelex' Choice Rank</h2>

      <p>
        XXX describe this.
      </p>

		  ${htmlgen.table_text( [ 'Player', "Nemelex' Choice Wins", 'Combos' ],
                           data, place_column=1, skip=True )}
	  </div>
  </div>
</%block>
