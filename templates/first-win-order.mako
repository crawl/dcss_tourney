<%inherit file="base.mako"/>

<%!
  import html
  import query

  active_menu_item = None
%>

<%block name="title">
  Time of First Win Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Time of First Win Ranking</h2>
      <p>
        The first win of every player in the tournament, ranked by finish
        time-of-day. Players who have not yet won do not appear in this
        ranking.
      </p>

		  ${html.games_table( query.first_win_order(c, limit = None),
                        first = 'end_time', place_column = 1, skip = True,
                        excluding = ['runes'],
                        win = True, highlight_wins = False)}
	  </div>
  </div>
</%block>
