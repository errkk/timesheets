$(document).ready(function(){
	// Delete warnong message

	$('.deletewarning').on('click', function(e){
		var answer = confirm('Whoa steady on sonny! This will get totes deleted, you sure bruvs?');
		if( answer ){
			window.location.href = this.href;
		}
		e.preventDefault();
	});

	// Put the JQ datepicker on the date field if the field type is not supported
	(function(){
		var i = document.createElement('input');
		i.setAttribute('type','date');

		if( 'date' !== i.type ){
			// Date filters, UI box
			$( "#date_filters input[type='date']" ).datepicker({
				showButtonPanel: true,
				dateFormat: 'yy-mm-dd'
			});
		}
	}());


	

	// Redirect URL from form submission, so URL is pretty for custom date filter inputs
	$('#date_filters').on('submit',function(e){
		var $form = $(this),
		date_from = $form.find('#date_from').val(),
		date_to = $form.find('#date_to').val();

		window.location = base_url + date_from + "/" + date_to;

		e.preventDefault();
	});


	// Redirect URL from form submission, so URL is pretty for month selectbox
	$('#months').on('submit',function(e){
		var $form = $(this),
		month = $form.find('#month').val();

		window.location = base_url + month;

		e.preventDefault();
	});




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
			  url: '/gs/ajax/',
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




$(document).ready(function(){

	var dropbox = document.getElementById("dropbox"),
	$target	= $(dropbox),
	url_dump = '/gs/dump';

	if( !dropbox ){
		return false;
	}


	// init event handlers
	dropbox.addEventListener("dragenter", dragEnter, false);
	dropbox.addEventListener("dragexit", dragExit, false);
	dropbox.addEventListener("dragover", dragOver, false);
	dropbox.addEventListener("drop", drop, false);

	function dragEnter(evt) {
		evt.stopPropagation();
		evt.preventDefault();

	}

	function dragExit(evt) {
		$target.removeClass('over');
		evt.stopPropagation();
		evt.preventDefault();
	}

	function dragOver(evt) {
		$target.addClass('over');
		evt.stopPropagation();
		evt.preventDefault();
	}

	function noopHandler(evt) {
		$target.removeClass('over');
		evt.stopPropagation();
		evt.preventDefault();
	}

	function drop(evt){

		$target.removeClass('over').addClass('dropped');
		evt.stopPropagation();
		evt.preventDefault();

		var files = evt.dataTransfer.files;
		var count = files.length;

		// Only call the handler if 1 or more files was dropped.
		if (count > 0){
			handleFiles(files);
		}
	}

	function handleFiles(files){
		var file = files[0],
		label = document.getElementById("droplabel"),
		original_message = label.innerHTML;

		if( 'text/xml' !== file.type ){
			label.innerHTML = 'Please drag the XML file from Grindstone';
			$target.removeClass().addClass('error');
			resetBG();
			return;
		}else{
			label.innerHTML = "Processing " + file.name;	
		}


		var reader = new FileReader();

		// init the reader event handlers
		reader.onload = function(evt) {
			$target.addClass('loading');
			$.ajax({
			  type: 'POST',
			  url: url_dump,
			  data: evt.target.result,
			  success: function(res){
			  	var data = JSON.parse(res); 
			  	$target.removeClass('loading');

			  	if( 'ok' === data.status ){
			  		var $list = $('#list').html('');
				  	$(data.data).each(function(i,item){
							var $li = $('<li>');
							$list.append( $li.html( item['name'] + ' ' + item['total'] ) ); 
				  	});
				  	label.innerHTML = "Your Tasks";
			  	}else if( 'uptodate' === data.status ){
			  		label.innerHTML = "Already got this :-)";
			  	}
			  	$target.removeClass().addClass('dropped');

			  	resetBG();

			  },
			  error: function(data){
			  	$target.removeClass().addClass('error');
			  	resetBG();
			  }
			});
		}

		function resetBG(){
			window.setTimeout(function(){ 
				$target.removeClass(); 
				label.innerHTML = original_message;
			}, 3000 );

		}

		// begin the read operation
		reader.readAsDataURL(file);

		
	}

});