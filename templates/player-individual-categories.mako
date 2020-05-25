<%page args="rank_description"/>

<%
  from crawl_utils import XXX_IMAGE_BASE
  import html
  import scoring_data
%>

<h2>Individual Categories</h2>
% for category in scoring_data.INDIVIDUAL_CATEGORIES:
<%
  results = individual_category_results[category.name]
%>
<div class="row">
  <div class="col">
    <div class="jumbotron category category-image text-light p-3" style="background-image: linear-gradient(to right, rgba(0,0,0,0.4) 31%, rgba(0,0,0,1) 33%), url('${XXX_IMAGE_BASE}/individual/${html.slugify(category.name)}.png');">
      <h2 class="text-outline-black-1">${category.name}</h2>
      <div class="row">
        <div class="col col-sm-4">
          <h3 class="text-outline-black-1">${rank_description(results.rank)}</h3>
        </div>
        <div class="col-sm">
          <p class="d-none d-sm-block">
            <i>${category.desc}</i>
          </p>
          % if results.details is not None:
          <p class="lead">
            ${results.details}
          </p>
          % endif
          % if category.url:
          <p class="small">
            <a href="${category.url}">
              View full ranking.
            </a>
          </p>
          % endif
        </div>
      </div>
    </div>
  </div>
</div>
% endfor
