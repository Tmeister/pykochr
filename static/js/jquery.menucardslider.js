jQuery(document).ready(function($){

	window.cardcontainer = $('#card-container');
	window.cardnext = $('#card-next');
	window.cardprev = $('#card-prev');
	window.activepage = cardcontainer.attr('activepage');
	cardcontainer.animate({
		height: $('#cardpageid-' + window.activepage).height() + 40
	}, 0 );

	var marginLeft = ((window.activepage-1)*956)*-1;
	$('#card-slider').css("left",marginLeft);
	window.totalPages = $('.card-page').size();

	window.blockAnimation = false;
	$('#card-next, #card-prev').click(function(){
		direction = $(this).attr('id')
		
		if ( direction == 'card-next' ){
		if (window.activepage != window.totalPages){
			cardNavigation(false)
			}
		} else {
		if (window.activepage != 1){
			cardNavigation(true)
		}
		}
		return false
	});


});
 
function cardNavigation(prev){
	marginLeft = ((window.activepage-1)*950)*-1;
	if (window.blockAnimation == false) {
		window.blockAnimation = true;
		if ( prev == true ){
			window.activepage--;
		} else {
			window.activepage++;
		}	
		
		left = ( prev == true ) ? (marginLeft + 950) : (marginLeft - 950)
		$('#card-slider').fadeOut(400);
		$('#card-slider').animate({
			left: left
		}, 0, function(){
			
			window.blockAnimation = false;
			
		});
		$('#card-slider').fadeIn(400);
		window.cardcontainer.attr('activepage', window.activepage).animate({
			height: $('#cardpageid-' + window.activepage).height() + 40
		}, 400 );
	}
}