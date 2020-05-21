<%
  import html
%>

<h2>Banners</h2>

<div class="row row-cols-sm-1 row-cols-xl-2">
  % for banner in banners:
  <div class="col mb-4">
    <div class="card h-100 banner text-light">
      <img src="/images/altar/${html.slugify(banner['god'])}.png" class="card-img-top pixel-art px-5 mt-3 mx-auto" style="max-width: 240px;" alt="${banner['god']}">
      <div class="card-body">
        <h2 class="card-title">${banner['name']}</h2>
        <ul class="list-group list-group-flush">
          % for tier in range(0,3):
          <%
            achieved = banner['achieved'] > tier
          %>
          <li class="list-group-item bg-dark py-1">
            % if achieved:
            <img src="/images/gui/prompt_yes.png" class="float-left mr-1" alt="Tier achieved">
            % endif
            <p class="lead mb-0">${'<s>' if achieved else ''}
              Tier ${tier + 1}: <small><i>${banner['tiers'][tier]}</i></small>
            ${'</s>' if achieved else ''}</p>
            <p class="mb-0">
              ${banner['tier_notes'][tier]}
            </p>
          </li>
          % endfor
        </ul>
      </div>
    </div>
  </div>
  % endfor
</div>
