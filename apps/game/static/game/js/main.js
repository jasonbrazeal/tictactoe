$(document).ready(function() {

    $('#board td').click(function(e) {
        var postData = {
            'space': $(this).attr('id'),
        };
        if ($(this).text() !== postData.player) {
            $(this).text(postData.player);

            $.ajax({
                url: '/play',
                type: 'POST',
                data: postData,
                dataType: 'json',
                beforeSend: function(){
                },
                success: function(responseData){
                    board = $.parseJSON(responseData.board)
                    $('h1').text(board);
                    $("#" + String(responseData.space_AI)).text(responseData.player_AI);
                }, /* success */
                error: function(jqXHR, textStatus, errorThrown){
                }, /* error */
                complete: function(){
                } /* complete */
            }); /* ajax call */
                // e.preventDefault(); // to stop default action
        }
    }); /* click */


}); /* document.ready */