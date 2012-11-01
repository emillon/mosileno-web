<%inherit file="base.mako"/>
<%!
from mosileno.filter import lx
%>
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
