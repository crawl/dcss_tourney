<%page args="points_for_result"/>

<%
  import crawl_utils
  from crawl_utils import XXX_IMAGE_BASE, base_link
  import html
  import scoring_data

  def rank_for_result(result, category):
    if category.proportional:
      return str("%d/%d" % (result.rank, category.max))
    elif category.transform_fn is not None:
      return category.transform_fn(result.rank)
    else:
      return "{:,}".format(result.rank)
%>

<h2>Individual Categories</h2>
<table class="table table-borderless table-dark table-striped table-hover w-auto">
  <thead>
    <tr>
      <th scope="col">Category</th>
      <th scope="col">Outcome</th>
      <th scope="col">Points</th>
      <!--<th scope="col">Notes</th>-->
    <tr>
  </thead>
  <tbody>
    ## First row shows total score
    <tr class="table-secondary">
      <th scope="row">
        <a href="${base_link('all-players-ranks.html')}">
          Total
        </a>
      </th>
      <th scope="row" class="text-monospace text-right">${overall_rank}</th>
      <th scope="row" class="text-monospace text-right">
        <%
        points = int(
          round(
            sum(
              float(points_for_result(individual_category_results[c.name], c)
	            or 0.0)
              for c in scoring_data.INDIVIDUAL_CATEGORIES
            )
          , 0)
        )
        %>
        ${'{:,}'.format(points)}
      </th>
      <!--<th scope="row"></th>-->
    </tr>
  % for category in scoring_data.INDIVIDUAL_CATEGORIES:
  <%
    results = individual_category_results[category.name]
  %>
    <tr>
      <td>
        <a href="${base_link(crawl_utils.slugify(category.name))}.html">
          ${category.name}
        </a>
      </td>
      <td class="text-monospace text-right">${rank_for_result(results,
      category) if results.rank else '-'}</td>
      <td class="text-monospace
      text-right">${'{:,}'.format(points_for_result(results, category)) if results.rank else '-'}</td>
      <!--<td>${results.details if results.details else ''}</td>-->
    </tr>
  % endfor
  </tbody>
</table>
