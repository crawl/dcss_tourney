<%page args="points_for_rank"/>

<%
  from crawl_utils import XXX_IMAGE_BASE, base_link
  import html
  import scoring_data
%>

<h2>Individual Categories</h2>
<table class="table table-borderless table-dark table-striped table-hover w-auto">
  <thead>
    <tr>
      <th scope="col">Category</th>
      <th scope="col">Rank</th>
      <th scope="col">Points</th>
      <th scope="col">Notes</th>
    <tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">
        <a href="${base_link('all-players-ranks.html')}">
          Total
        </a>
      </th>
      <th scope="row" class="text-monospace text-right">${overall_rank}</th>
      <th scope="row" class="text-monospace text-right">
        ${'{:,}'.format(sum(int(points_for_rank(result.rank)) for result in individual_category_results.values() if result.rank is not None))}
      </th>
      <th scope="row"></th>
    </tr>
  % for category in scoring_data.INDIVIDUAL_CATEGORIES:
  <%
    results = individual_category_results[category.name]
  %>
    <tr>
      <td>
        <a href="${base_link(html.slugify(category.name))}.html">
          ${category.name}
        </a>
      </td>
      <td class="text-monospace text-right">${results.rank if results.rank else '-'}</td>
      <td class="text-monospace text-right">${'{:,}'.format(int(points_for_rank(results.rank))) if results.rank else '-'}</td>
      <td>${results.details if results.details else ''}</td>
    </tr>
  % endfor
  </tbody>
</table>
