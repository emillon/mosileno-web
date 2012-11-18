<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>

<nav>
    <ul class="nav nav-list">
        <li class="nav-header">Views</li>
        <li class="active"><a href="#"><i class="icon-list"></i> All items</a></li>
        <li><a href="#"><i class="icon-list"></i> Relevant</a></li>
        <li class="nav-header">Feeds</li>
% for feed in feeds:
        <li>${feed.title}</li>
% endfor
    </ul>
</nav>

<div class="accordion" id="accordion2">
% for (item, genid) in items:
    <div class="accordion-group">
      <div class="accordion-heading">
        <a class="accordion-toggle" data-toggle="collapse"
           data-parent="#accordion2" href="#${genid}">
          ${item.title}
        </a>
      </div>
      <div id="${genid}" class="accordion-body collapse">
        <div class="accordion-inner">
          <a href="${item.link}">Go</a>
          ${item.description | n, lx}
        </div>
      </div>
    </div>
% endfor
</div>
