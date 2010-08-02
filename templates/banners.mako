<%
   import query, html
   c = attributes['cursor']

   all_banners = query.player_banners_awarded()
 %>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>${title}</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>
  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>
      <div class="page_content">

        <div class="banner-desc">
          <h2>Banners Awarded</h2>

          <hr>

          %for banner in all_banners:

          ${html.banner_img_for(banner[0], None)}

          <p>
            ${", ".join([crawl_utils.player_link(p) for p in banner[1]])}
          </p>

          %endfor
        </div>

      </div>
    </div>
    ${html.update_time()}
  </body>
</html>
