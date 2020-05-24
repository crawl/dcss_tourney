<%inherit file="base.mako"/>

<%!
  import scoring_data
  import html
  import query

  active_menu_item = None
%>

<%block name="title">
  Exploration Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Exploration Ranking</h2>
      <p>
		   In this category, players earn 3 points per distinct rune of Zot
		   collected and 1 point each for distinct branch or branch end entered.
      </p>

		  ${html.table_text( [ 'Player', 'Exploration Score' ],
          query.exploration_order(c), place_column=1, skip=True)}
	  </div>
  </div>
</%block>
