/*global $, jQuery */
/*jslint browser: true, indent: 4, sloppy: true, regexp: true, plusplus: true, continue: true, white: true, smarttabs: false */

/*!
 * Drag and drop function for consolodating tasks via ajax
 */
$(document).ready(function(){
	
	(function(){
		var $table = $('#dnd');
		if( !$table ){
			return false;
		}
		// Top scope stuff
		var $items = $table.find('tr'),
		drag_subject = false;


		// Style the thing that's being dragged
		function handleDragStart(e){
			if (e.stopPropagation) {
				e.stopPropagation();
			}
			this.style.opacity = '0.6';
			// Store this element at the top of the scope so the target knows what's landed on it
			drag_subject = this;
		}

		// Add hover classes, only for rows that arent the one being dragged
		function handleDragEnter(e){
			var target_id = $(this).data('id'),
			subject_id = $(drag_subject).data('id');
			if( target_id !== subject_id ){
				$(this).addClass('over');
			}
		}

		function handleDragOver(e){
			if (e.preventDefault) {
				e.preventDefault(); // Necessary. Allows us to drop.
			}
			e.dataTransfer.dropEffect = 'move';
		}

		// Not being hovered any more
		function handleDragLeave(e){
			$(this).removeClass('over');
		}

		// Handle something being dropped on an element
		function handleDrop(e){
			if (e.stopPropagation) {
				e.stopPropagation(); // stops the browser from redirecting.
			}
			// Find Ids of thing to change from and to
			var $target = $(this), 
			target_id = $(this).data('id'),
			subject_id = $(drag_subject).data('id');

			// Check its not been dropped on itselft
			if( target_id !== subject_id ){
				// Hide the thing that was being moved
				$(drag_subject).slideUp(500);
				$(this).removeClass('over');
				// Send Ajax request
				consolodate_tasks( subject_id, target_id, function(){
					var old_colour = $target.css('background'),
					$td = $target.find('td');
					
					$td.animate({
						'background-color':'#090',
						'color' : '#fff'
					}, 500, function(){
						$td.animate({
							'background-color' : old_colour,
							'color'	: '#000'
						}, 200 );
					});

				});
			}else{
				$(this).removeClass('over');
			}
			return false;
		}

		// Remove dragging stuff
		function handleDragEnd(e){
			this.style.opacity = '1';
			drag_subject = false;
		}

		// Send AJAX request to reassign aliases on the DB
		function consolodate_tasks( subject, target, success_callback ){
			$.ajax({
			  type: 'PUT',
			  url: ajax_url,
			  data: JSON.stringify({ 'subject' : subject, 'target' : target }),
			  success: function(res){
			  	var data = JSON.parse(res); 
			  	if( 'ok' === data.status ){
			  		if( 'function' === typeof success_callback ){
			  			success_callback(data.data);
			  		}
			  	}
			  },
			  error: function(data){
			  	window.location.href = window.location.href;
			  }
			});
		
		}

		// Bind drag events to each TR
		$items.each(function(i,el){
			el.addEventListener('dragstart', handleDragStart, false);
			el.addEventListener('dragenter', handleDragEnter, false)
			el.addEventListener('dragover', handleDragOver, false);
			el.addEventListener('dragleave', handleDragLeave, false);
			el.addEventListener('drop', handleDrop, false);
			el.addEventListener('dragend', handleDragEnd, false);
		});

	}());

});