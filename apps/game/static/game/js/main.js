$(document).ready(function() {

    function setupGame(postData) {
        $.ajax({
            url: '/setup',
            type: 'POST',
            data: postData,
            dataType: 'html',
            beforeSend: function(){
            },
            success: function(responseData){
                $('#board td').text();
                $('#board').fadeIn('slow');
            }, /* success */
            error: function(jqXHR, textStatus, errorThrown){
                $('h1').text(textStatus + ' ' + errorThrown);
            }, /* error */
            complete: function(jqXHR, textStatus){
                $('#has_game').text('True');
            } /* complete */
        }); /* ajax call */
    }

    $('#setup').click(function(e) {
        $('#dialog-setup').dialog({
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
            title: 'tic-tac-toe',
            buttons: {
              "I'll be Xs": function() {
                setupGame({'player_human': 'X'});
                $(this).dialog('close');
                $('#player_human').text('X')
              }, /* 'X' */
              "Gimme Os": function() {
                setupGame({'player_human': 'O'});
                $(this).dialog('close');
                $('#player_human').text('O')
              } /* 'O' */
            }, /* buttons */
            close: function() {
            } /* close */
        }); /* dialog */
    }); /* setup */

    $('#board td').click(function(e) {
        var postData = {
            'space_human': $(this).attr('id').substr(-1),
        };
        if (!$(this).text()) {
            $(this).text($('#player_human').text());
            $(this).removeClass('shaded');
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
                    $('#space' + String(responseData.space_AI)).text(responseData.player_AI);
                    if (responseData.winner) {
                        $('h1').text(responseData.winner + ' is the winner!!!');
                    } else if (responseData.tie) {
                        $('h1').text("tie...cat's game!!!");
                    }
                }, /* success */
                error: function(jqXHR, textStatus, errorThrown){
                        $('h1').text('error...please try your move again. (error info: ' + errorThrown + ' - ' + textStatus);
                        // $(this).text(''); // remove player's move on error
                }, /* error */
                complete: function(jqXHR, textStatus){
                        responseData = $.parseJSON(jqXHR.responseText);
                        if (responseData.winner || responseData.tie) {
                            $(function() {
                                $('#winner').text(responseData.winner);
                                if (responseData.tie) {
                                    $('#cat').show(); // show grumpy cat
                                } else {
                                    $('#winner').append('s'); // make X or O plural
                                }
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
                                    title: 'tic-tac-toe',
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

    $('#reset').click(function() {
        window.location.reload();
    }); /* reset/refresh */

    $('#board td').hover(
        function() {
            if (!$(this).text()) {
                $(this).addClass('shaded');
            }
        },
        function() {
            $(this).removeClass('shaded');
        }
    ); /* hover */

    if ($('#has_game').text()) {
        $('#dialog-continue').dialog({
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
            title: 'tic-tac-toe',
            buttons: {
                "Sure": function() {
                    $(this).dialog('close');
                    $('#board').fadeIn('slow');
                },
                "Nah...start over": function() {
                    clearSession();
                }
            }, /* buttons */
            close: function() {
            } /* close */
        }); /* dialog */
    } /* has game */

   function clearSession() {
        $.ajax({
            url: '/clear',
            type: 'POST',
            data: '',
            dataType: 'html',
            beforeSend: function(){
            },
            success: function(responseData){
                $('#has_game').text();
                window.location.reload();
            }, /* success */
            error: function(jqXHR, textStatus, errorThrown){
            }, /* error */
            complete: function(jqXHR, textStatus){
            } /* complete */
        }); /* ajax call */
    }
}); /* document.ready */