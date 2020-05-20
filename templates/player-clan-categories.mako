<%page args="rank_description"/>

<h2>Clan Categories</h2>
% for category in clan_categories:
<%
  import html
  name = category['name']
  css_class = "cat-clan-%s" % html.slugify(name)
  rank_desc = rank_description(category['rank'])
%>
<div class="row">
  <div class="col">
    <div class="jumbotron jumbotron-fluid category ${css_class} text-light p-3">
      <h2 class="text-outline-black-1">${name}</h2>
      <div class="row">
        <div class="col col-sm-4">
          <h3 class="text-outline-black-1">${rank_desc}</h3>
        </div>
        <div class="col-sm">
          <p class="d-none d-sm-block">
            <i>${category['desc']}</i>
          </p>
          <p class="lead">
            ${category['rank_details']}
          </p>
        </div>
      </div>
    </div>
  </div>
</div>
% endfor
