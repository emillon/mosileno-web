<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Mosileno</title>
        <link rel="shortcut icon"
              href="${request.static_url('mosileno:static/favicon.ico')}"
          />
        <link rel="stylesheet"
              href="${request.static_url('mosileno:static/css/bootstrap.css')}"
              type="text/css"
              media="screen"
              charset="utf-8"
          />
        <link rel="stylesheet"
              href="${request.static_url('mosileno:static/css/mosileno.css')}"
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

            <script type="text/javascript"
                    src="${request.static_url('mosileno:static/post.js')}"
            ></script>
    </head>
    <body>

      <div class="navbar navbar-inverse">
        <div class="navbar-inner">
          <div class="container" style="width: auto;">
            <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
            </a>
            <a class="brand" href="/about">
              <img src="${request.static_url('mosileno:static/cloverfeed_white_tiny.png')}"
                   style="width:19px; vertical-align:top"/>
              Cloverfeed
            </a>
            <div class="nav-collapse">
              <ul class="nav">
                <li data-tabname="home"><a href="/">Home</a></li>
                <li data-tabname="expandedview"><a href="/expandedview">Expanded view</a></li>
                <li data-tabname="addsrc"><a href="/feed/add">Add a source</a></li>
              </ul>
              <ul class="nav pull-right">
                % if logged_in is None:
                    <li><a href="/signup">Sign up</a></li>
                    <li><a href="/login">Login</a></li>
                % else:
                    <li data-tabname="profile"><a href="/profile">You're ${logged_in}</a>
                    <li><a href="/logout">Logout</a></li>
                % endif
              </ul>
            </div><!-- /.nav-collapse -->
          </div>
        </div><!-- /navbar-inner -->
      </div><!-- /navbar -->

      <div id='maincontainer' class="container-fluid">
        % if errors:
        % for error in errors:
            <div class="alert alert-error">
            ${error}
            </div>
        % endfor
        % endif
        ${self.body()}
      </div>

      <script type="text/javascript"
              src="${request.static_url('mosileno:static/jquery-1.8.2.min.js')}"
       ></script>
      <script type="text/javascript"
              src="${request.static_url('mosileno:static/bootstrap.min.js')}"
       ></script>
% if activetab:
      <script type="text/javascript">
          $('[data-tabname="${activetab}"]').addClass('active');
      </script>
% endif
% if activeview:
      <script type="text/javascript">
          $('[data-activeview="${activeview}"]').addClass('active');
      </script>
% endif
    </body>
</html>
