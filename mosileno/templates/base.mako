<html>
    <head>
        <title>Mosileno</title>
        <link rel="stylesheet"
              href="${request.static_url('mosileno:static/mosileno.css')}"
              type="text/css"
              media="screen"
              charset="utf-8"
          />
          % for reqt in (css_links or []):
            <link rel="stylesheet"
                  href="${request.static_url('deform:static/%s' % reqt)}"
                  type="text/css" />
          % endfor
          % for reqt in (js_links or []):
            <script type="text/javascript"
                    src="${request.static_url('deform:static/%s' % reqt)}"
             ></script>
          % endfor
    </head>
    <body>
        <div class=headerCont>
            <ul class=headerLeft>
                <li><a href="/feed/add">Add a feed</a></li>
                <li><a href="/feed/add/opml">Import OPML file</a></li>
                <li><a href="/feeds/my">My feeds</a></li>
            </ul>
            <ul class=headerRight>
                % if logged_in is None:
                    <li><a href="/signup">Sign up</a></li>
                    <li><a href="/login">Login</a></li>
                % else:
                    <li><a href=#>You're ${logged_in}</a>
                    <li><a href="/logout">Logout</a></li>
                % endif
                <li>
            </ul>
        </div>
        <div id=main>
            ${self.body()}
        </div>
        <div class=footer>
            <ul>
                <li><a href=#>About us</a></li>
            </ul>
        </div>
    </body>
</html>
