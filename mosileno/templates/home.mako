<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>

<div class="row-fluid">

    <div class="span11">
    % for (item, genid, feedtitle) in items:
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
                    <div class="itemfeed">${feedtitle}</div>
                </div>
            </a>
        </div>
    % endfor
    </div>

</div>
