$(function($) {
	
	$(".input-tooltip").tipTip({activation: 'focus', maxWidth: "auto", edgeOffset: 5, defaultPosition:'left'});
	$(".login-tooltip").tipTip({activation: 'focus', maxWidth: "auto", edgeOffset: 5, defaultPosition:'top'});
	$(".subtooltip, .toptooltip").tipTip({maxWidth: "auto", edgeOffset: 5, defaultPosition:'top'});
	$('#sendavatar').click(function(event) {
		event.preventDefault();
		$('#uploadavatar').submit();
	});

	$('#user_login, #user_pass').focus(function(){
		$('.error-password').html('');
	})
			

	$('#top-login, #top-register, #create-account').click(function(event) {
		event.preventDefault();
		switch($(this).attr('id')){
			case 'top-login':
				$('#login-form').modal();
			case 'top-register':
			case 'create-account':
				$('#register-form').modal();

		}
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
		    			location.href = location.href
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
					location.href = location.href
				}


		  	}
		});		
	});

	$('#save_settings').click(function(event) {
		event.preventDefault();
		$('#form_settings').submit();

	});

	
	if ( $("#koch_notes").length ) {
		$("#koch_notes").ata();
		$('#koch_ingredient').bubbleBox();
		$('#koch_directions').bubbleBox();
		$('#koch_tags').bubbleBox();	
	};
	

	$('.field.info-box-red').hide();
	$('.field.info-box-green').hide();
	$('#koch_name, #koch_ingredient, #koch_directions, #koch_notes').focus(function(){
		$('.field.info-box-red').slideUp('slow');
	});

	function show_error (error) {
		$('.info-box-red .koch_status').html(error);
		$('.field.info-box-red').show();
	}
	function show_success (error) {
		$('.info-box-green .koch_status').html(error);
		$('.field.info-box-green').show();
	}


	$('#koch_save').click(function(e) {
		e.preventDefault();
		name = 		$.trim( $('#koch_name').val() );
		ingredients = 	$('#koch_ingredient_list > li');
		directions = 	$('#koch_directions_list > li');
		tags = 		$('#koch_tags_list > li');
		notes = 		$('#koch_notes').val();

		if( ! name.length ){show_error('Really, Do you not forget the name?');return;}
		if( notes.length < 50 ){show_error('Please write a description at least 50 chars about your recipe');return;}
		if( ! ingredients.length ){show_error('A recipe without ingredients is it strange, Huh?');return;}
		if( ! directions.length ){show_error('We need directions to get it right');return;}


		ingredients_to_go = [];
		ingredients.each(function(){
			//ingredients_to_go.push( $(this).find('span').html() );
			var hidden = $('<input/>',{name:'ingredients[]',type:'hidden',value:$(this).find('span').html()});
			hidden.appendTo($('#form_new_koch'));
		});

		directions_to_go = [];
		directions.each(function(){
			var hidden = $('<input/>',{name:'directions[]',type:'hidden',value:$(this).find('span').html()});
			hidden.appendTo($('#form_new_koch'));
		});

		tags_to_go = [];
		tags.each(function(){
			var hidden = $('<input/>',{name:'tags[]',type:'hidden',value:$(this).find('span').html()});
			hidden.appendTo($('#form_new_koch'));
		});

		$('#form_new_koch').submit()

	});

	$('.follow-trigger').click(function(event) {
		event.preventDefault()
		target = $(this).find('a');
		target = $( target[0] );
		key = target.attr('data-key');
	});
			
			

	$('.ajax-like-trigger').click(function(event) {
		event.preventDefault();
		target = $(this).find('a');
		target = $( target[0] );
		key = target.attr('data-key');
		if( target.hasClass('like') ){
			up_vote( target, key )
			return 
		}
		if( target.hasClass('liked') ){
			down_vote( target, key )
			return 
		}
	});

	$('.ajax-follow-trigger').click(function(event) {
		event.preventDefault();
		target = $(this).find('a');
		target = $( target[0] );
		fan = target.attr('data-fan');
		star = target.attr('data-star');
		if (target.hasClass('follow-button')){
			do_follow( target, fan, star )
			return
		};
		if (target.hasClass('unfollow-button')){
			do_unfollow( target, fan, star )
			return
		};
	});
			
			

	function do_follow (target, key) {
		$.ajax({
			url: '/ajax/follow',
			type: 'POST',
			dataType: 'json',
			data: {
				fan : fan,
				star : star
			},
			success: function(data, textStatus, xhr) {
				user_message('Now you are following to ' + data.star, 'success');
				link = '<a href="#" class="unfollow-button block small-size" data-fan="'+ String(data.fan_key) +'" data-star="'+String(data.star_key)+'">Unfollow</a>';
				target.parent().html(link);
				$('.followers span').html( data.star_followers +' Followers')
			}
		});					
	}

	function do_unfollow (target, key) {
		$.ajax({
			url: '/ajax/unfollow',
			type: 'POST',
			dataType: 'json',
			data: {
				fan : fan,
				star : star	
			},
			success: function(data, textStatus, xhr) {
				user_message('Unfollow ' + data.star, 'success');
				link = '<a href="#" class="follow-button block small-size" data-fan="'+String(data.fan_key)+'" data-star="'+String(data.star_key)+'">Follow</a>';
				target.parent().html(link);
				$('.followers span').html( data.star_followers +' Followers')
						
			}
		});
		
	}


	function up_vote(target, key) {
		$.ajax({
			url: '/ajax/up-vote',
			type: 'POST',
			dataType: 'json',
			data: {
				key : key
			},
			success: function(data, textStatus, xhr) {
				if( data.status == 'success' ){
					target.parent().html( '<a href="#" title="You like this, Click to unlike" class="liked" data-key="'+key+'">'+data.votes+' Likes</a>' );
				}else{
					user_message(data.message, 'error');
				}

			}
		});
	}

	function down_vote (target, key) {
		$.ajax({
			url: '/ajax/down-vote',
			type: 'POST',
			dataType: 'json',
			data: {
				key : key
			},
			success: function(data, textStatus, xhr) {
				if( data.status == 'success' ){
					target.parent().html( '<a href="#" title="You like this, Click to unlike" class="like" data-key="'+key+'">'+data.votes+' Likes</a>' );
				}else{
					user_message(data.message, 'error');
				}
			}
		});
	}

	function user_message( message, theme ){
		$.jGrowl(message, {theme:theme, position: 'bottom-right'});
	}
});

/***************************************************
			Nivo Slider
***************************************************/
/*jQuery.noConflict()(function($){
$(document).ready(function() {
            $('#slider').nivoSlider({
                pauseTime:5000,
                pauseOnHover:false
            });        
    });
});*/
/***************************************************
			SuperFish Menu
***************************************************/	
// initialise plugins
	jQuery.noConflict()(function(){
		jQuery('ul.sf-menu').superfish();
	});

/***************************************************
			PRETTY PHOTO
***************************************************/
/*jQuery.noConflict()(function($){
$(document).ready(function() {  

$("a[rel^='prettyPhoto']").prettyPhoto({opacity:0.80,default_width:500,default_height:344,theme:'light_rounded',hideflash:false,modal:false});

});
});*/
/***************************************************
			LIST SLIDER
***************************************************/
/*jQuery.noConflict()(function($){
		$(document).ready(function() {

			$.featureList(
				$("#tabs li a"),
				$("#output li"), {
					start_item	:	1
				}
			);
		});
});
*/
/***************************************************
			ACCORDION SLIDER
***************************************************/
/*jQuery.noConflict()(function($){
				$('.kwicks').kwicks({
					max : 900,
					spacing : 0
				});
			});*/
			
			
/***************************************************
			MOSAIC
***************************************************/
/*jQuery.noConflict()(function($){
				
				$('.circle').mosaic({
					opacity		:	0.8			//Opacity for overlay (0-1)
				});
				
				$('.fade').mosaic();
				
				$('.bar').mosaic({
					animation	:	'slide'		//fade or slide
				});
				
				$('.bar2').mosaic({
					animation	:	'slide'		//fade or slide
				});
				
				$('.bar3').mosaic({
					animation	:	'slide',	//fade or slide
					anchor_y	:	'top'		//Vertical anchor position
				});
				
				$('.cover').mosaic({
					animation	:	'slide',	//fade or slide
					hover_x		:	'400px'		//Horizontal position on hover
				});
				
				$('.cover2').mosaic({
					animation	:	'slide',	//fade or slide
					anchor_y	:	'top',		//Vertical anchor position
					hover_y		:	'100px'		//Vertical position on hover
				});
				
				$('.cover3').mosaic({
					animation	:	'slide',	//fade or slide
					hover_x		:	'400px',	//Horizontal position on hover
					hover_y		:	'300px'		//Vertical position on hover
				});
		    
		    });		*/	
/***************************************************
			IMAGE HOVER
***************************************************/
jQuery.noConflict()(function($){
$(document).ready(function() {  
            $('.img-preview').each(function() {
                $(this).hover(
                    function() {
                        $(this).stop().animate({ opacity: 0.5 }, 400);
                    },
                   function() {
                       $(this).stop().animate({ opacity: 1.0 }, 400);
                   })
                });
});
});
/*
jQuery.noConflict()(function($){
			$('#slides').slides({
				preload: true,
				generateNextPrev: false
			});
			$('#slides2').slides({
				preload: true,
				generateNextPrev: false,
				generatePagination: true
			});
		});
*/