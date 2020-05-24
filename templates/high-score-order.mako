<%inherit file="base.mako"/>

<%!
  import html
  import query

  active_menu_item = None
%>

<%block name="title">
  Best High Score Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Best High Score Ranking</h2>

		  ${html.games_table( query.high_score_order(c, limit = None),
                        first = 'score', place_column = 1, skip = True )}
	  </div>
  </div>
</%block>
