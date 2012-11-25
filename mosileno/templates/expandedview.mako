<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>

<div class="row-fluid">

    <div class="span9">
    % for (item, genid, feedtitle) in items:
        <div class="itemfull">
                <a onclick="$.post('/signal', {'source': 'expandedview', 'action': 'linkclick', 'item': '${item.id}'})" href="${item.link}">
                    <div class="itemtitle">${item.title}</div>
                </a>
                <div class=itembody>
                    ${item.description | n, lx}
                </div>
            <div class="itemfooter">
                <div class="vote-arrow">
                    <img id="up_${genid}" 
onmouseover="document.getElementById('up_${genid}').src = '${request.static_url('mosileno:static/arrows/up_arrow_hover.png')}'"
onclick="document.getElementById('up_${genid}').src = '${request.static_url('mosileno:static/arrows/up_arrow_clicked.png')}'; $.post('/signal', {'source': 'expandedview', 'action': 'linkup', 'item': '${item.id}'})" 
src="${request.static_url('mosileno:static/arrows/up_arrow_normal.png')}" width="18"/>
                </div>
                <div class="vote-arrow">
                    <img id="down_${genid}" 
onmouseover="document.getElementById('up_${genid}').src = '${request.static_url('mosileno:static/arrows/down_arrow_hover.png')}'"
onclick="document.getElementById('down_${genid}').src = '${request.static_url('mosileno:static/arrows/down_arrow_clicked.png')}'; $.post('/signal', {'source': 'expandedview', 'action': 'linkdown', 'item': '${item.id}'})" 
src="${request.static_url('mosileno:static/arrows/down_arrow_normal.png')}" width="18"/>
                </div>
                <div class="itemtopics">
                    topic1, topic2
                </div>
                <div class="itemadditionallinks">
                    link to comments or social network conversation
                </div>
                <div class="itemsource">
                    <div class="itemfeed">${feedtitle}</div>
                </div>
            </div>
        </div>
    % endfor
    </div>

    <div class="span2">
            <ul class="nav nav-list">
                <li class="nav-header">View</li>
                <li data-activeview="all"><a href="/expandedview"><i class="icon-list"></i> All</a></li>
                <li data-activeview="relevant"><a href="#"><i class="icon-filter"></i> Filtered</a></li>
        % if manage:
                <li class="nav-header">Manage</li>
                <li><a href="/feed/${manage.slug}/unsubscribe"><i class="icon-remove-circle"></i> Unsubscribe</a></li>
        %endif
                <li class="nav-header">Feeds</li>
        % for feed in feeds:
                <li data-activeview="${'feed-%s' % feed.slug}"><a href="/feed/${feed.slug}">${feed.title}</a></li>
        % endfor
            </ul>
    </div>

</div>
