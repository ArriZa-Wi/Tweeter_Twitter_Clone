$(document).ready(function () {
    $(".like_button").click(function (event) {
        // The work we want to do on click

        // Get required data
        let target = $(event.currentTarget);
        let twit_id = target.data('id');
        let twit_action = target.data('action');
        let twit_like_url = target.data('like-url');

        // Get icon <i> and count <span> elements so that we can update if person liked it
        let like_icon = target.find('.like_icon');
        let like_count = target.find('.like_count');

        $.ajax({
            url: twit_like_url,
            data: {
                twit_id: twit_id,
                twit_action: twit_action,
            },
        }).done(function (data) {
            if (data.success) {
                // if we liked, update element to match
                if (twit_action === 'like') {
                    // DO like
                    target.removeClass('btn-outline-primary');
                    target.addClass('btn-primary');
                    like_icon.removeClass('bi-hands-thumbs-up');
                    like_icon.addClass('bi-hands-thumbs-up-fill');
                    like_count.html(Number(like_count.html()) + 1);
                    target.data('action', 'unlike');
                } else {
                    target.removeClass('btn-primary');
                    target.addClass('btn-outline-primary');
                    like_icon.removeClass('bi-hands-thumbs-up-fill');
                    like_icon.addClass('bi-hands-thumbs-up');
                    like_count.html(Number(like_count.html()) - 1);
                    target.data('action', 'like');
                }
            }
        });
    });
});