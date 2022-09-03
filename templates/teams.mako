<%inherit file="base.mako"/>

<%!
  import scoring_data
  import tourney_html as html
  import query

  active_menu_item = "Clans"
%>

<%block name="title">
  Clans
</%block>

<%block name="main">
  <%
    c = attributes['cursor']
    stats = query.get_all_clan_ranks(c)
  %>
  <div class="row">
    <div class="col">
      <h1>Clans</h1>

      ${html.table_text(
        [ 'Clan', 'Members', 'Overall Score' ] + [ html.category_column_title(cc) for cc in scoring_data.CLAN_CATEGORIES ],
        data=stats, place_column=2, skip=False, extra_wide_support=True,
        datatables=True )
      }
    </div>
  </div>
</%block>
