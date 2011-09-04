$(function($) {
	$('#top-login, #top-register').click(function(event) {
		event.preventDefault();
		target = ( $(this).attr('id') == 'top-login' ) ? $('#login-form') : $('#register-form');
		target.modal({
			onOpen: 	function(dialog){
				dialog.overlay.fadeIn( 'slow', function(){
					dialog.data.hide();
					dialog.container.fadeIn( 'slow', function(){
						dialog.data.slideDown('slow')
					});
				});
			},
			onClose: 	function(dialog){
				$('#account-loader').hide();
				dialog.data.slideUp('slow', function () {
					dialog.container.fadeOut('slow', function () {
						dialog.overlay.fadeOut('slow', function () {
							$.modal.close();
						});
					});
				});
			}
		});//modal close
	});

	$('#showregistersubmit').click(function(event) {
		event.preventDefault();
		targetBtn = $(this);
		//targetBtn.attr('disabled', 'disabled');
		$('.error-register').html('');
		$('#account-loader').show();
		$.ajax({
		  	url: '/ajax/register' ,
		  	type: 'POST',
		  	dataType: 'json',
		  	data: {
			  email: 	$('#register-email').val(),
			  username: $('#register-username').val(),
			  password: $('#register-password').val()
			},
		  	success: function(data, textStatus, xhr) {
		    		targetBtn.removeAttr('disabled');
		    		$('#account-loader').hide();
		    		if( data.status == 'error' ){
		    			$('.error-register').html( data.message );
		    		}
		    		if( data.status == 'success' ){
		    			location.href = '/'
		    			//$('#register-form .loginbuttons').html('<p class="success_message">' + data.message+ '</p>');
		    		}
			}
	 	});
	});

	$('#loginsubmit').click(function(event) {
		event.preventDefault();
		targetBtn = $(this);
		targetBtn.attr('disabled', 'disabled');
		$('.error-register').html('');
		$('#login-loader').show();
		$.ajax({
			url: '/ajax/login',
			type: 'POST',
			dataType: 'json',
			data: {
				username: $('#user_login').val(), 
				passwd:$('#user_pass').val()
			},
		  	success: function(data, textStatus, xhr) {
				targetBtn.removeAttr('disabled');
				if( data.status == 'error' ){
	    			$('.error-password').html( data.message );
	    		}
				if( data.status == 'success' ){
					location.href = '/'
				}

				
		  	}
		});		
	});
			
			


});
