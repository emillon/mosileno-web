<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>

<div class="row-fluid">

    <div class="span11">
    % for (item, genid, feedtitle) in items:
        <div class="itemheader">
            <div class="pull-left">
                <img id="up_${genid}" 
onclick="document.getElementById('up_${genid}').style.visibility = 'hidden'; $.post('/linkup', '${item.link}')" 
src="${request.static_url('mosileno:static/up_gray_tiny.png')}"
style="height:10px; vertical-align:middle"/>
                <img id="down_${genid}" 
onclick="document.getElementById('down_${genid}').style.visibility = 'hidden'; $.post('/linkdown', '${item.link}')" 
src="${request.static_url('mosileno:static/down_gray_tiny.png')}"
style="height:10px; vertical-align:middle"/>
            </div>
            <a onclick="$.post('/linkclick', '${item.link}')" href="${item.link}">
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
