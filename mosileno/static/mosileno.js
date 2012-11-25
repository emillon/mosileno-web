function signal(page, id, action) {
    var data = {'source': page,
                'action': action,
                'item': id
               };
    $.post('/signal', data);
}
