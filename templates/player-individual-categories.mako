<%page args="rank_description"/>

<%
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
    <div class="jumbotron category category-image text-light p-3" style="background-image: linear-gradient(to right, rgba(0,0,0,0.2) 31%, rgba(0,0,0,1) 33%), url('/images/individual/${html.slugify(category.god)}.png');">
      <h2 class="text-outline-black-1">${category.god}</h2>
      <div class="row">
        <div class="col col-sm-4">
          <h3 class="text-outline-black-1">${rank_description(results.rank)}</h3>
        </div>
        <div class="col-sm">
          <p class="d-none d-sm-block">
            <i>${category.desc}</i>
          </p>
          <p class="lead">
            ${results.details}
          </p>
        </div>
      </div>
    </div>
  </div>
</div>
% endfor
