$(document).ready(function() {

    $('#board td').click(function(e) {
        var postData = {
            'space_human': $(this).attr('id'),
            'player_human': 'X',
        };
        if (!$(this).text()) {
            $(this).text(postData.player_human);

            $.ajax({
                url: '/play',
                type: 'POST',
                data: postData,
                dataType: 'json',
                beforeSend: function(){
                    // block user form clicking on tds while this request is processing
                },
                success: function(responseData){
                    // board = $.parseJSON(responseData.board) # python list
                    $('#' + String(responseData.space_AI)).text(responseData.player_AI);
                    if (responseData.winner) {
                        $('h1').text(responseData.winner + ' is the winner!!!');
                    } else if (responseData.tie) {
                        $('h1').text("tie...cat's game!!!");
                    }
                }, /* success */
                error: function(jqXHR, textStatus, errorThrown){
                        $('h1').text('error...please try your move again. (error info: ' + errorThrown + ' - ' + textStatus);
                }, /* error */
                complete: function(jqXHR, textStatus){
                        responseData = $.parseJSON(jqXHR.responseText);
                        if (responseData.winner || responseData.tie) {
                            $(function() {
                                $('#dialog-confirm').dialog({
                                    resizable: false,
                                    modal: true,
                                    autoOpen: true,
                                    width: '500px',
                                    height: '100px',
                                    dialogClass: 'dialog' ,
                                    position: {
                                        my: 'center top',
                                        at: 'center top',
                                        of: $('html'),
                                    },
                                    title: responseData.winner ? responseData.winner + ' is the winner!' : "It's a tie...cat's game!",
                                    buttons: {
                                      'Yes': function() {
                                        $(this).dialog('close');
                                        window.location.reload();
                                      },
                                      'Exit': function() {
                                        $(this).dialog('close');
                                        window.location = '/thanks';
                                      }
                                    } /* buttons */
                                 }); /* dialog */
                            });
                        } /* if game over */
                } /* complete */
            }); /* ajax call */
                // e.preventDefault(); // to stop default action
        }
    }); /* make a play */

    $('#reset').click(function(e) {
        window.location.reload();
    }); /* reset/refresh */

}); /* document.ready */