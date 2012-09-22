<%
   import query, html, crawl_utils

   c = attributes['cursor']

   all_banners = query.player_banners_awarded(c)
   title = "Banners Awarded"
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

        <div class="banner-desc banner-top-padded">
          <h2>Banners Awarded</h2>

          <hr>

          %for ban in all_banners:
          <% img = html.banner_named(ban[0], ban[1]) %>
            %if img:
            ${img}
            <div class="text">
              <h3>${html.banner_image(ban[0], ban[1], full_name=True)[1]}</h3>
              ${", ".join([crawl_utils.linked_text(p[0],crawl_utils.player_link,p[0]+(len(p[1]) > 0 and ("("+",".join(p[1])+")") or "")) for p in ban[2]])}
            </div>
            <hr>
            %endif
          %endfor
        </div>

      </div>
    </div>
    ${html.update_time()}
  </body>
</html>
