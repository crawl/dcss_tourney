<%inherit file="base.mako"/>

<%!
  import htmlgen
  import query

  active_menu_item = None
%>

<%block name="title">
  Lowest Turn-count Win Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Lowest Turn-count Win Ranking</h2>

		  ${htmlgen.games_table( query.low_turncount_win_order(c, limit = None),
                        first = 'turn', place_column = 1, skip = True )}
	  </div>
  </div>
</%block>
