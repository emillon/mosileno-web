<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>

<div class="row-fluid">

    <div class="span9">
    % for (item, genid, feed) in items:
        <div class="itemfull">
                <a onclick="$.post('/linkclick', '${item.link}')" href="${item.link}">
                    <div class="itemtitle">${item.title}</div>
                </a>
                <div class=itembody>
                    ${item.description | n, lx}
                </div>
            <div class="itemfooter">
                <div class="pull-left">
                    <div class="vote-arrow">
                        <img id="up_${genid}" 
    onclick="document.getElementById('up_${genid}').style.visibility = 'hidden'; $.post('/linkup', '${item.link}')" 
    src="${request.static_url('mosileno:static/up_gray_tiny.png')}" width="16"/>
                    </div>
                    <div class="vote-arrow">
                        <img id="down_${genid}" 
    onclick="document.getElementById('down_${genid}').style.visibility = 'hidden'; $.post('/linkdown', '${item.link}')" 
    src="${request.static_url('mosileno:static/down_gray_tiny.png')}" width="16"/>
                    </div>
                </div>
                <div class="itemtopics">
                    topic1, topic2
                </div>
                <div class="itemadditionallinks">
                    link to comments or social network conversation
                </div>
                <div class="pull-right">
                    <div class="itemfeed">
                      <a href="/feed/${feed.slug}">
                        ${feed.title}
                      </a>
                    </div>
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
