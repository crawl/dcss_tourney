<%page args="rank_description"/>

<%
  from crawl_utils import XXX_IMAGE_BASE
  import html
  import scoring_data
%>

<h2>Individual Categories</h2>
<div class="row row-cols-md-2">
  % for category in scoring_data.INDIVIDUAL_CATEGORIES:
  <%
    results = individual_category_results[category.name]
  %>
  <div class="col mb-4">
    <div class="card h-100 bg-dark text-light">
      <img
        src="${XXX_IMAGE_BASE}/individual/${html.slugify(category.name)}.png"
        alt=""
        class="card-img"
        style="filter: brightness(40%);">
      <div class="card-img-overlay">
        <h2 class="card-title">${category.name}</h2>
        <p class="card-text lead">
          ${rank_description(results.rank)}
        </p>
        <p class="card-text">
          <i>${category.desc}</i>
        </p>
        % if results.details is not None:
        <p class="card-text lead">
          ${results.details}
        </p>
        % endif
        <p class="card-text small">
          % if category.url:
          <a href="${category.url}">
            View full ranking.
          </a>
          % else:
          Full ranking not available for this category.
          % endif
        </p>
      </div>
    </div>
  </div>
  % endfor
</div>
