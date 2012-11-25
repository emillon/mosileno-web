function signal(page, id, action) {
    var data = {'source': page,
                'action': action,
                'item': id
               };
    $.post('/signal', data);
}

function upvote(page, item_id, img_id) {
    var clicked = '/static/arrows/up_arrow_clicked.png';
    $(img_id).attr('src', clicked);
    $(img_id).unbind('mouseenter mouseleave');
    signal(page, item_id, 'linkup');
}

function downvote(page, item_id, img_id) {
    var clicked = '/static/arrows/down_arrow_clicked.png';
    $(img_id).attr('src', clicked);
    $(img_id).unbind('mouseenter mouseleave');
    signal(page, item_id, 'linkdown');
}

function mosileno_main() {
    $(".rollover").hover(function(){
        // mouse over
        img_src = $(this).attr('src');
        new_src = $(this).attr('data-rollover');
        $(this).attr('src', new_src);
        $(this).attr('data-rollover', img_src);
    },
    function(){
        //mouse out
        $(this).attr('src', img_src);
        $(this).attr('data-rollover', new_src);
    });
}

$(document).ready(mosileno_main);
