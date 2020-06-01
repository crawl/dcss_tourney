<%
  from crawl_utils import XXX_IMAGE_BASE
  import html
  import scoring_data
%>

<h2>Banners</h2>

<div class="row row-cols-1 row-cols-md-2 row-cols-xl-3">
  % for banner in scoring_data.BANNERS:
  <%
    results = banner_results[banner.name]
  %>
  <div class="col mb-4">
    <div class="card h-100 banner bg-dark text-light">
      <img src="${XXX_IMAGE_BASE}/altar/${html.slugify(banner.god)}.png" class="card-img-top pixel-art px-5 mt-3 mx-auto" style="max-width: 180px;" alt="${banner.god}">
      <div class="card-body">
        <h2 class="card-title">${banner.name}</h2>
        <ul class="list-group list-group-flush">
          % for tier in (1, 2, 3):
          <%
            achieved = results.tier >= tier
          %>
          <li class="list-group-item bg-dark py-1">
            % if achieved:
            <img src="${XXX_IMAGE_BASE}/gui/prompt_yes.png" class="float-left mr-1" alt="Tier achieved">
            % endif
            <p class="lead mb-0">${'<s>' if achieved else ''}
              Tier ${tier}: <small><i>${banner.tiers[tier - 1]}</i></small>
            ${'</s>' if achieved else ''}</p>
            <p class="mb-0">
              ${results.details[tier - 1]}
            </p>
          </li>
          % endfor
        </ul>
      </div>
    </div>
  </div>
  % endfor
</div>
