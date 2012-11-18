<%inherit file="base.mako"/>
%if info:
%if len(info) == 1:
<div class="alert alert-success">
    ${info[0]}
</div>
%else:
<div class="alert alert-success">
%for i in info:
    <li>${i}</li>
%endfor
</div>
%endif
%endif:
${form | n}
