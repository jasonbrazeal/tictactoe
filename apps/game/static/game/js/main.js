$(document).ready(function() {

    $('#board td').click(function(e) {
        var postData = {
            'position': $(this).attr('id'),
            'player': 'X'
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