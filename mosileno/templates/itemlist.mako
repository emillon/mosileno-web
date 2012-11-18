<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>

<nav>
    <ul class="nav nav-list">
        <li class="nav-header">View</li>
        <li class="${activelink('all')}"><a href="/feeds/my"><i class="icon-list"></i> All</a></li>
        <li class="${activelink('relevant')}"><a href="#"><i class="icon-filter"></i> Filtered</a></li>
        <li class="nav-header">Feeds</li>
% for feed in feeds:
        <li class="${activelink('feed%d' % feed.id)}" ><a href="/feed/${feed.id}">${feed.title}</a></li>
% endfor
    </ul>
</nav>

<div>
% for (item, genid, feedtitle) in items:
    <div class="itemfull">
        <div class="itemheader">
            <a onclick="$('#${genid}').toggle()" href=#>
                <div class="itemtitle">${item.title}</div>
                <div class="pull-right">
                    <div class="itemfeed">${feedtitle}</div>
                    <i class="icon-thumbs-up"></i>
                    <i class="icon-thumbs-down"></i>
                </div>
            </a>
        </div>
        <div id="${genid}" style='display:none'>
          <div>
            <a href="${item.link}">Go</a>
            ${item.description | n, lx}
          </div>
        </div>
    </div>
% endfor
</div>
