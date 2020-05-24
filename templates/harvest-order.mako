<%inherit file="base.mako"/>

<%!
  import html
  import query

  active_menu_item = None
%>

<%block name="title">
  Harvest Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Harvest Ranking</h2>
      <p>
        In this category, players earn 1 point for each distinct unique
        killed and 1 point for each player ghost killed.
      </p>

		  ${html.table_text( [ 'Player', 'Harvest Score' ],
   							query.harvest_order(c), place_column=1, skip=True)}
	  </div>
  </div>
</%block>
