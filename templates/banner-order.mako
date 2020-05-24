<%inherit file="base.mako"/>

<%!
  import scoring_data
  import html
  import query

  active_menu_item = None
%>

<%block name="title">
  Banner Score Ranking
</%block>


<%block name="main">
  <%
    c = attributes['cursor']
  %>
  <div class="row">
    <div class="col">
      <h2>Banner Score Ranking</h2>
      <p>
        Each god awards a banner with three tiers, banner tiers award 1, 2,
        or 4 points in this category.
      </p>

      ${html.table_text( [ 'Player', 'Banner Score', 'Banners Earned' ],
                      query.banner_order(c), place_column=1, skip=True)}
    </div>
  </div>
</%block>
