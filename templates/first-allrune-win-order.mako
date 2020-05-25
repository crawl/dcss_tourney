<%inherit file="base.mako"/>

<%!
  import htmlgen
  import query

  active_menu_item = None
%>

<%block name="title">
  Time of First All-Rune Win Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Time of First All-Rune Win Ranking</h2>
      <p>
        The first all-rune win of every player in the tournament, ranked by
        finish time-of-day. Players who have not yet won an all-rune game do
        not appear in this ranking.
      </p>

		  ${htmlgen.games_table( query.first_allrune_win_order(c, limit = None),
                        first = 'end_time', place_column = 1, skip = True,
                        excluding = ['runes'],
                        win = True)}
	  </div>
  </div>
</%block>
