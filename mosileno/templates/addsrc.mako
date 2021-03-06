<%inherit file="base.mako"/>
<div class="container">
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
%endif

<h2>Add a RSS feed</h2>

Here you can enter the URL of a website that you would like to follow. It can be
either the URL of the feed itself (often ending in <code>.xml</code>), or the
adress of the site itself.

${form_rss | n}
<h2>Import OPML data</h2>

OPML files represent a set of subscriptions. For example, you can export OPML
data from your account on Google Reader or Netvibes and import it here. 

${form_opml | n}
<h2>Connect Reddit</h2>

<a href="http://reddit.com">Reddit</a> is a social website where users post
links and vote to elect the most popular ones. You can connect a particular
subreddit community.

${form_reddit | n}
</div>
