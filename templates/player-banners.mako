<h2>Banners</h2>

% for banner in banners:
<div class="row">
  <div class="col">
    <div class="jumbotron banner banner-${banner['god']} text-light p-3">
      <h2>${banner['name']}<br><small>${banner['god']}</small></h2>
      <div class="row">
        <div class="col-3">
          <img class="pixel-art banner-image" src="/images/banner-${banner['god']}.png">
        </div>
        <div class="col">
          <ul class="list-unstyled">
            <li class="${'bg-success' if banner['achieved'] > 0 else 'bg-danger'}">Tier 1: ${banner['tiers'][0]}</li>
            <li class="${'bg-success' if banner['achieved'] > 1 else 'bg-danger'}">Tier 2: ${banner['tiers'][0]}</li>
            <li class="${'bg-success' if banner['achieved'] > 2 else 'bg-danger'}">Tier 3: ${banner['tiers'][0]}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>

% endfor
