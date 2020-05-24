<%inherit file="base.mako"/>

<%!
  import html
  import query

  active_menu_item = None
%>

<%block name="title">
  Win Percentage Ranking
</%block>

<%block name="main">
<%
   c = attributes['cursor']
%>
  <div class="row">
    <div class="col">
      <h2>Win Percentage Ranking</h2>
      <p>
        Win percentage is calculated as:
        <pre>
          number of wins / ( number of games played + 1 )
        </pre>
      </p>

		  ${html.table_text( [ 'Player', 'Win Percentage' ],
   							query.win_perc_order(c), place_column=1, skip=True)}
	  </div>
  </div>
</%block>
