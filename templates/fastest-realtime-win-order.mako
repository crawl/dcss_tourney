<%inherit file="base.mako"/>

<%!
  import scoring_data
  import htmlgen
  import query

  active_menu_item = None
%>

<%block name="title">
  Fastest Real-time Win Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Fastest Real-time Win Ranking</h2>

		  ${htmlgen.games_table( query.fastest_win_order(c, limit = None),
          first = 'duration', place_column = 1, skip = True,
          win = True)}
	  </div>
  </div>
</%block>
