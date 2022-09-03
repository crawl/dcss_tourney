<%
  import crawl_utils
  from crawl_utils import XXX_IMAGE_BASE
  import tourney_html as html
  import scoring_data
%>

<h2>Banners</h2>

<p>
  Banners give points in the individual & clan banner categories.
  Banner tiers are worth 1, 2, and 4 points for tiers one, two, and
  three respectively.
</p>

<table class="table table-borderless table-dark table-striped table-hover w-auto">
  <thead>
    <tr>
      <th scope="col">Banner</th>
      <th scope="col">Tier One</th>
      <th scope="col">Tier Two</th>
      <th scope="col">Tier Three</th>
    <tr>
  </thead>
  <tbody>
  % for banner in scoring_data.BANNERS:
  <%
    results = banner_results[banner.name]
  %>
    <tr>
      <td>
        <img
          src="${XXX_IMAGE_BASE}/altar/${crawl_utils.slugify(banner.god)}.png"
          alt="${banner.god}"
          class="pixel-art"
          loading="lazy"
        >
        ${banner.name}
      </td>
      % for tier in range(3):
      <%
        achieved = results.tier > tier
      %>
      <td>
        % if achieved:
        <img src="${XXX_IMAGE_BASE}/gui/prompt_yes.png" class="float-left mr-1" alt="Tier ${tier + 1} achieved">
        % endif
        <p class="small">
          ${'<s>' if achieved else ''}
          <b>
            Tier ${tier + 1}:
          </b>
          ${banner.tiers[tier]}
          ${'</s>' if achieved else ''}
        </p>
      </td>
      % endfor
  % endfor
  </tbody>
</table>
