<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>

<div class="row-fluid">

    <div class="span11">
    % for (item, genid, feed) in items:
        <div class="itemshort">
            <div class="vote-arrow">
                <img id="up_${genid}"
                    class="rollover"
                    src="/static/up_gray_tiny.png"
                    data-rollover="/static/arrows/up_arrow_hover.png"
                    onclick="upvote('home', '${item.id}', '${genid}')"
                    width="18"
                    />
            </div>
            <div class="vote-arrow">
                <img id="down_${genid}"
                    class="rollover"
                    src="/static/down_gray_tiny.png"
                    data-rollover="/static/arrows/down_arrow_hover.png"
                    onclick="downvote('home', '${item.id}', '${genid}')"
                    width="18"
                    />
            </div>
            <a onclick="signal('home', '${item.id}', 'linkclick')"
               href="${item.link}"
               class="itemshortbody">
                <div class="itemtitle">${item.title}</div>
                <div class="itemdomain">domain.com</div>
                <div class="itemsource">
                    <div class="itemfeed">${feed.title}</div>
                </div>
            </a>
        </div>
    % endfor
        <script type='text/javascript'>
            var data = [];
    % for (item, genid, feed) in items:
            dd = {'id': ${item.id}, 'data': '${genid}'};
            data.push(dd);
    % endfor
            //console.log(data)
            $.post('/vote', JSON.stringify(data), function(r) {
                $.each(r, function(i, x) {
                    if (x.vote === 1) {
                        arrow_inactive('#up_' + x.data, 'up');
                    }
                    if (x.vote === -1) {
                        arrow_inactive('#down_' + x.data, 'down');
                    }
                    console.log(x.vote);
                });
            });
        </script>
    </div>

</div>
