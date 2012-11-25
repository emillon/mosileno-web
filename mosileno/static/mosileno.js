function signal(page, id, action) {
    var data = {'source': page,
                'action': action,
                'item': id
               };
    $.post('/signal', data);
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
