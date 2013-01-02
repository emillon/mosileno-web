<%inherit file="base.mako"/>
<table class="table table-condensed">
<thead>
    <tr>
        <td>#</td>
        <td>Title</td>
        <td>Actions (Async)</td>
        <td>Actions (Sync)</td>
    </tr>
</thead>
<tbody>
%for feed in feeds:
    <tr>
        <td>${feed.id}</td>
        <td>${feed.title}</td>
        <td>
            <a class="btn" href="/admin/${feed.slug}/trigger/fetch_title">fetch_title</a>
            <a class="btn" href="/admin/${feed.slug}/trigger/fetch_items">fetch_items</a>
        </td>
        <td>
            <a class="btn" href="/admin/${feed.slug}/trigger/fetch_title?sync">fetch_title</a>
            <a class="btn" href="/admin/${feed.slug}/trigger/fetch_items?sync">fetch_items</a>
        </td>
    </tr>
%endfor
</tbody>
</table>
