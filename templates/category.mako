<%page args="category,data"/>
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
</%block>
