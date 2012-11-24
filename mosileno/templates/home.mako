<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>

<div class="row-fluid">

    <div class="span11">
    % for (item, genid, feedtitle) in items:
        <div class="itemheader">
            <div class="pull-left">
                <div class="vote-arrow">
                    <img id="up_${genid}" 
    onclick="document.getElementById('up_${genid}').style.visibility = 'hidden'; $.post('/signal', {'source': 'home', 'action': 'linkup', 'item': '${item}'})" 
    src="${request.static_url('mosileno:static/up_gray_tiny.png')}" width="16"/>
                </div>
                <div class="vote-arrow">
                    <img id="down_${genid}" 
    onclick="document.getElementById('down_${genid}').style.visibility = 'hidden'; $.post('/signal', {'source': 'home', 'action': 'linkdown', 'item': '${item}'})" 
    src="${request.static_url('mosileno:static/down_gray_tiny.png')}" width="16"/>
                </div>
            </div>
            <a onclick="$.post('/signal', {'source': 'home', 'action': 'linkclick', 'item': '${item}'})" href="${item.link}">
                <div class="itemtitle">${item.title}</div>
                <div class="itemdomain">domain.com</div>
                <div class="pull-right">
                    <div class="itemfeed">${feedtitle}</div>
                </div>
            </a>
        </div>
    % endfor
    </div>

</div>
