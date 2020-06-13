<%page args="category,data"/>
<%inherit file="base.mako"/>

<%!
  import scoring_data
  import html
  import query
  import crawl_utils

  active_menu_item = None
%>

<%block name="preprocess">
<%
  # TODO: not sure if this is really the best way to accomplish this?
  if category.type == "clan":
    self.attr.active_menu_item = "Clan Categories"
  else:
    self.attr.active_menu_item = "Player Categories"
%>
</%block>

<%block name="title">
  <%
    page_title = "%s%s Ranking" % ("Clan " if category.type == "clan" else "", category.name)
  %>
  ${page_title}
</%block>


<%block name="main">
  <%
    page_title = "%s%s Ranking" % ("Clan " if category.type == "clan" else "", category.name)
  %>
  <div class="row">
    <div class="col">
      <h2>${page_title}</h2>
      <img
        src="${crawl_utils.XXX_IMAGE_BASE}/${category.type}/${crawl_utils.slugify(category.name)}.png"
        alt=""
        class="rounded img-thumbnail"
        ## Smallest image is 250x250
        style="background: black; max-width: 250px;"
      >
      <p>
        ${category.desc}
      </p>
      % if category.name == "Nemelex' Choice":
        <%include file="nemelex-choice-overview.mako"/>
      % endif
      % if category.source_table:
      ${
        html.category_table(
          category,
          rows,
        )
      }
      % endif
    </div>
  </div>
  % if category.name == "Streak Length" and category.type == "individual":
  <div class="row">
    <div class="col">
      <h2>Top Active Streaks</h2>
      <p>
      Currently active streaks. Note: a player's currently active streak may
      not be their current best streak.
      </p>
      ${html.best_active_streaks(cursor)}
    </div>
  </div>
  % endif

</%block>
