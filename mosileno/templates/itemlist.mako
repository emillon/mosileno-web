<%inherit file="base.mako"/>
<ul>
% for item in items:
    <li>
        <a href="${item.link}">${item.title}</a>
    </li>
% endfor
</ul>
