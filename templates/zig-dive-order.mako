<%inherit file="base.mako"/>

<%!
  import htmlgen
  import query

  active_menu_item = None
%>

<%block name="title">
  Ziggurat Dive Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Ziggurat Dive Ranking</h2>

		  ${htmlgen.table_text( [ 'Player', 'Ziggurats Completed', 'Deepest Floor in last Ziggurat'],
   							query.zig_dive_order(c), place_column=3, skip=True)}
	  </div>
  </div>
</%block>
