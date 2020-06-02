<%page args="category"/>
<%inherit file="base.mako"/>

<%!
  import scoring_data
  import html
  import query
  import crawl_utils

  active_menu_item = None
%>

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
        src="${crawl_utils.XXX_IMAGE_BASE}/${category.type}/${html.slugify(category.name)}.png"
        alt=""
        class="rounded img-thumbnail"
        ## Smallest image is 250x250
        style="background: black; max-width: 250px;"
      >
      <p>
        ${category.desc}
      </p>
      ## Hack to disable Ziggurat Diving as it breaks
      % if category.source_table and category.name != 'Ziggurat Diving':
      <%
        columns = ['Player' if category.type == 'individual' else 'Clan', category.source_column_name]
        for col in category.full_ranking_extra_columns:
          columns.append(col.display_name)
      %>
      ${html.table_text(
          columns,
          scoring_data.category_leaders(category, cursor),
          place_column=1,
          skip=True)
      }
      % endif
    </div>
  </div>
</%block>
