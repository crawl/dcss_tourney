<%inherit file="base.mako"/>

## Run on template load (no render context)
<%!
  import scoring_data
  import html
  import query

  active_menu_item = "Players"
%>

## Runs on render. Variables set in here are not accessible to <%blocks>. To
## make data available, write it to a key in the empty dict 'attributes', which
## was passed in at template render time.
## <%
## %>

## The rest of the template is blocks or body (an implicit block called body).
## Access any top level variables passed in as render args, including the dict
## 'attributes' mentioned in the <% %> section comments above.
<%block name="title">
  All Players
</%block>

<%block name="main">

  <%
    c = attributes['cursor']
    stats = query.get_all_player_ranks(c)
  %>
  <div class="row">
    <div class="col">
      <h1>All Players</h1>

      ${html.table_text(
        [ 'Player', 'Clan', 'Overall Score' ] + [ html.category_column_title(ic) for ic in scoring_data.INDIVIDUAL_CATEGORIES ],
        data=stats, place_column=2, skip=False, extra_wide_support=True,
        datatables=True )
      }
    </div>
  </div>
</%block>
