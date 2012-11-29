function signal(page, id, action) {
    var data = {'source': page,
                'action': action,
                'item': id
               };
    $.post('/signal', data);
}

function arrow(dir, state) {
    if (state === 'plain') {
        return ('/static/' + dir + '_gray_tiny.png');
    }
    return '/static/arrows/' + dir + '_arrow_' + state + '.png';
}

function arrow_active(sel, dir) {
    $(sel).attr('src', arrow(dir, 'plain'));
    rollover_on(sel);
}

function arrow_inactive(sel, dir) {
    $(sel).attr('src', arrow(dir, 'clicked'));
    rollover_off(sel);
}

function vote(dir, page, item_id, genid) {
    var other_dir;
    if (dir === 'up') {
        other_dir = 'down';
    } else {
        other_dir = 'up';
    }
    var clicked = arrow(dir, 'clicked');
    var img_id = '#' + dir + '_' + genid;
    var cur_src = $(img_id).attr('src');
    var other_id = '#' + other_dir + '_' + genid;
    var other_src = $(other_id).attr('src');

    if (cur_src === arrow(dir, 'clicked')) {
        // cancel vote
        arrow_active(img_id, dir)
        signal(page, item_id, 'link' + dir + 'cancel');
    } else {
        // register vote
        if (other_src === arrow(other_dir, 'clicked')) {
            arrow_active(other_id, other_dir);
        }
        arrow_inactive(img_id, dir);
        signal(page, item_id, 'link' + dir);
    }
}

function display_votes(data) {
    $.post('/vote', JSON.stringify(data), function(r) {
        $.each(r, function(i, x) {
            if (x.vote === 1) {
                arrow_inactive('#up_' + x.data, 'up');
            }
            if (x.vote === -1) {
                arrow_inactive('#down_' + x.data, 'down');
            }
            console.log(x.vote);
        });
    });
}

function upvote(page, item_id, genid) {
    vote('up', page, item_id, genid)
}

function downvote(page, item_id, genid) {
    vote('down', page, item_id, genid)
}

function rollover_off(selector) {
    $(selector).unbind('mouseenter mouseleave');
}

function rollover_on(selector) {
    function flip(sel) {
        var img_src = $(sel).attr('src');
        var new_src = $(sel).attr('data-rollover');
        $(sel).attr('src', new_src);
        $(sel).attr('data-rollover', img_src);
    }
    $(selector).hover(function(){
        // mouse over
        flip(this);
    },
    function(){
        //mouse out
        flip(this);
    });
}

function mosileno_main() {
    rollover_on(".rollover");
}

$(document).ready(mosileno_main);
