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
                    onmouseover="document.getElementById('up_${genid}').src = '${request.static_url('mosileno:static/arrows/up_arrow_hover.png')}'"
                    onclick="document.getElementById('up_${genid}').src = '${request.static_url('mosileno:static/arrows/up_arrow_clicked.png')}'; $.post('/signal', {'source': 'home', 'action': 'linkup', 'item': '${item.id}'})"
                    src="${request.static_url('mosileno:static/up_gray_tiny.png')}"
                    width="18"
                    />
            </div>
            <div class="vote-arrow">
                <img id="down_${genid}"
                    onmouseover="document.getElementById('down_${genid}').src = '${request.static_url('mosileno:static/arrows/down_arrow_hover.png')}'"
                    onclick="document.getElementById('down_${genid}').src = '${request.static_url('mosileno:static/arrows/down_arrow_clicked.png')}'; $.post('/signal', {'source': 'home', 'action': 'linkdown', 'item': '${item.id}'})"
                    src="${request.static_url('mosileno:static/down_gray_tiny.png')}"
                    width="18"
                    />
            </div>
            <a onclick="$.post('/signal', {'source': 'home', 'action': 'linkclick', 'item': '${item.id}'})"
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
