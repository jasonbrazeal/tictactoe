$(document).ready(function() {

// get screen size for positioning dialog boxes
var screenSize;

if (Modernizr.mq('only screen and (max-width: 767px)')) {
    screenSize = 'small_screen';
    $('#dialog-continue').text('Continue?');
}

if (Modernizr.mq('only screen and (min-width: 768px) and (max-width: 1199px)')) {
    screenSize = 'med_screen';
}

if (Modernizr.mq('only screen and (min-width: 1200px)')) {
    screenSize = 'big_screen';
}

// part of the dialogs' look is configured in the CSS, e.g. internal height (.ui-dialog-content)
var dialogSetupConfig = {
                             'big_screen': {'my': 'center top',
                                            'at': 'center+125 top+60',
                                            'width': '625px',
                                            'height': '130px !important'},
                             'med_screen': {'my': 'center top',
                                            'at': 'center top+175',
                                            'width': '625px',
                                            'height': '130px !important'},
                             'small_screen': {'my': 'center top',
                                              'at': 'center top+100',
                                              'width': '300px',
                                              'height': '150px !important'},
                             };

var dialogConfirmConfig = {
                             'big_screen': {'my': 'center top',
                                            'at': 'center+100 top+60',
                                            'width': '625px',
                                            'height': '130px !important'},
                             'med_screen': {'my': 'center top',
                                            'at': 'center top+120',
                                            'width': '625px',
                                            'height': '130px !important',
                                            'boardTop': '+=50',
                                            'boardTopCat': '+=475'},
                             'small_screen': {'my': 'center top',
                                              'at': 'center top+73',
                                              'width': '300px',
                                              'height': '150px !important',
                                              'boardTop': '+=50',
                                              'boardTopCat': '+=450'},
                             };

var dialogContinueConfig = {
                             'big_screen': {'my': 'center top',
                                            'at': 'center+100 top+60',
                                            'width': '625px',
                                            'height': '130px !important',
                                            'startOverText': 'Nah...start over'},
                             'med_screen': {'my': 'center top',
                                            'at': 'center top+170',
                                            'width': '625px',
                                            'height': '130px !important',
                                            'startOverText': 'Nah...start over'},
                             'small_screen': {'my': 'center top',
                                              'at': 'center top+95',
                                              'width': '300px',
                                              'height': '150px !important',
                                              'startOverText': 'Nah...'},
                             };



// highlights start button when you hover over it
    $('#start').hover(function() {
        $('#start').addClass('ui-state-hover');
    }, function() {
        $('#start').removeClass('ui-state-hover');
    });

// starts the game by showing dialog to choose Xs or Os
// calls setupGame function
    $('#start').click(function(e) {
        $('#dialog-setup').dialog({
            resizable: false,
            modal: false,
            autoOpen: true,
            closeOnEscape: false,
            width: dialogSetupConfig[screenSize].width,
            height: dialogSetupConfig[screenSize].height,
            dialogClass: 'dialog',
            position: {
                my: dialogSetupConfig[screenSize].my,
                at: dialogSetupConfig[screenSize].at,
                of: $('html'),
            },
            title: '',
            buttons: {
              "I'll be Xs": function() {
                setupGame({'player_human': 'X'});
                $(this).dialog('close');
                $('#player_human').text('X');
              }, /* 'X' */
              "Gimme Os": function() {
                setupGame({'player_human': 'O'});
                $(this).dialog('close');
                $('#player_human').text('O');
              } /* 'O' */
            }, /* buttons */
            close: function() {
                $('#start').css('visibility', 'hidden');
            } /* close */
        }); /* dialog */
    }); /* start */

// makes ajax call to save new game session to database
// fades in board if successful
    function setupGame(postData) {
        $.ajax({
            url: '/tictactoe/setup',
            type: 'POST',
            data: postData,
            dataType: 'html',
            beforeSend: function(){
            },
            success: function(responseData){
                $('#board td').text('');
                $('#board').fadeIn('slow');
            }, /* success */
            error: function(jqXHR, textStatus, errorThrown){
                console.log(textStatus + ' ' + errorThrown);
            }, /* error */
            complete: function(jqXHR, textStatus){
                $('#has_game').text('True');
            } /* complete */
        }); /* ajax call */
    }

// handles click on any tic-tac-toe space
    $('#board td').click(function(e) {
        var postData = {
            'space_human': $(this).attr('id').substr(-1),
        };
        var isAvailable = !$(this).text();
        makePlay(postData, isAvailable);
    }); /* click on td */

// makes ajax call to save player's move to database, check win/tie, get AI's move, and check again for win/tie
// if win/tie, shows results and 'continue playing' dialog, otherwise makes AI's move
    function makePlay(postData, isAvailable) {
        if (isAvailable) {
            $('#space' + postData.space_human).text($('#player_human').text());
            $('#space' + postData.space_human).removeClass('shaded');
            $.ajax({
                url: '/tictactoe/play',
                type: 'POST',
                data: postData,
                dataType: 'json',
                beforeSend: function(){
                    $('#loading').show();
                },
                success: function(responseData){
                    // board = $.parseJSON(responseData.board) # python list
                    $('#space' + String(responseData.space_AI)).text(responseData.player_AI);
                    if (responseData.winner) {
                        console.log(responseData.winner + ' is the winner!!!');
                    } else if (responseData.tie) {
                        console.log("tie...cat's game!!!");
                    }
                }, /* success */
                error: function(jqXHR, textStatus, errorThrown){
                        console.log('error info: ' + errorThrown + ' - ' + textStatus);
                        // $(this).text(''); // remove player's move on error
                }, /* error */
                complete: function(jqXHR, textStatus){
                        $('#loading').hide();
                        responseData = $.parseJSON(jqXHR.responseText);
                        if (responseData.winner || responseData.tie) {
                            $(function() {
                                $('#winner').text(responseData.winner);
                                if (responseData.tie) {
                                    $('#cat').show(); // show grumpy cat
                                    $("#board").animate({
                                        top: dialogConfirmConfig[screenSize].boardTopCat
                                        }, 0, function() {
                                        // Animation complete.
                                    });
                                } else {
                                    $('#winner').append('s'); // make X or O plural
                                    $("#board").animate({
                                        top: dialogConfirmConfig[screenSize].boardTop
                                        }, 0, function() {
                                        // Animation complete.
                                    });
                                }
                                $('#dialog-confirm').dialog({
                                    resizable: false,
                                    modal: true,
                                    autoOpen: true,
                                    closeOnEscape: false,
                                    width: dialogConfirmConfig[screenSize].width,
                                    height: dialogConfirmConfig[screenSize].height,
                                    dialogClass: 'dialog',
                                    position: {
                                        my: dialogConfirmConfig[screenSize].my,
                                        at: dialogConfirmConfig[screenSize].at,
                                        of: $('#wrapper'),
                                    },
                                    title: '',
                                    buttons: {
                                      'Yeah': function() {
                                        window.location.reload();
                                      },
                                      'Nope': function() {
                                        window.location = '/thanks';
                                      }
                                    } /* buttons */
                                 }); /* dialog */
                            });
                        } /* if game over */
                } /* complete */
            }); /* ajax call */
        } /* if space not taken */
    } /* makePlay */

// shades board space when you hover over it
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

// detects if user already has a game in progress and brings up 'continue game' dialog and board if so
    if ($('#has_game').text()) {
        $('#start').css('visibility', 'hidden');
        $('#board').fadeIn('slow');
        $('#dialog-continue').dialog({
            resizable: false,
            modal: true,
            autoOpen: true,
            closeOnEscape: false,
            width: '550px',
            width: dialogContinueConfig[screenSize].width,
            height: dialogContinueConfig[screenSize].height,
            dialogClass: 'dialog',
            position: {
                my: dialogContinueConfig[screenSize].my,
                at: dialogContinueConfig[screenSize].at,
                of: $('html'),
            },
            title: '',
            buttons: [
                {
                    text: "Sure", click: function() {
                    $(this).dialog('close');
                    }
                },
                {
                    text: dialogContinueConfig[screenSize].startOverText, click: function() {
                    clearSession();
                    }
                }
            ], /* buttons */
            close: function() {
            } /* close */
        }); /* dialog */
    } /* has game */

// makes ajax call to clear django session then reloads page
   function clearSession() {
        $.ajax({
            url: '/tictactoe/clear',
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
                console.log('error info: ' + errorThrown + ' - ' + textStatus);
            }, /* error */
            complete: function(jqXHR, textStatus){
            } /* complete */
        }); /* ajax call */
    }

}); /* document.ready */