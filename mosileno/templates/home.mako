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
                    src="${request.static_url('mosileno:static/up_gray_tiny.png')}"
                    data-rollover="${request.static_url('mosileno:static/arrows/up_arrow_hover.png')}"
                    onclick="$('#up_${genid}').attr('src', '${request.static_url('mosileno:static/arrows/up_arrow_clicked.png')}'); signal('home', '${item.id}', 'linkup')"
                    width="18"
                    />
            </div>
            <div class="vote-arrow">
                <img id="down_${genid}"
                    class="rollover"
                    src="${request.static_url('mosileno:static/down_gray_tiny.png')}"
                    data-rollover="${request.static_url('mosileno:static/arrows/down_arrow_hover.png')}"
                    onclick="$('#down_${genid}').attr('src', '${request.static_url('mosileno:static/arrows/down_arrow_clicked.png')}'); signal('home', '${item.id}', 'linkdown')"
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
