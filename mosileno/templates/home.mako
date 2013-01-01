<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>

<div class="row-fluid">

    <div class="span11">
    % for (item, genid, feed, score) in items:
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
            </a>
                <div class="itemdomain" id="${genid}_domain"></div>
                <div class="itemsource">
                    <div class="progress pull-right" style="width: 60px">
                        <div class="bar" style="width: ${score_width(score)}%">
                        </div>
                    </div>
                    <div class="itemfeed">${feed.title}</div>
                </div>
        </div>
    % endfor
        <script type='text/javascript'>
            var data = [];
    % for (item, genid, feed, score) in items:
            dd = {'id': ${item.id}, 'data': '${genid}'};
            data.push(dd);
            $('#' + '${genid}' + '_domain').html(
                '(' + $('<a>').prop('href', '${item.link}').prop('hostname') + ')'
            );
    % endfor
            display_votes(data);
        </script>
    </div>

</div>
