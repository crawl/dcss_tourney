<%inherit file="base.mako"/>

<%!
  import htmlgen
  import query

  active_menu_item = None
%>

<%block name="title">
  Piety Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Piety Ranking</h2>
      <p>
        Players earn one point for becoming the champion (****** piety) and
        an additional point for a win after chapioning that god. Two gods
        (Gozag and Xom) do not have the usual ****** piety system; to get the
        points for these gods, you must never worship another god during the
        game.
      </p>

		  ${htmlgen.table_text( [ 'Player', 'Gods Championed', 'Gods Won', 'Piety Score' ],
   							query.piety_order(c), place_column=3, skip=True)}
	  </div>
  </div>
</%block>
