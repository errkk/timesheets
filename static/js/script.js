$(document).ready(function(){
	// Delete warnong message

	$('.deletewarning').on('click', function(e){
		var answer = confirm('Whoa steady on sonny! This will get totes deleted, you sure bruvs?');
		if( answer ){
			window.location.href = this.href;
		}
		e.preventDefault();
	});

	// Date filters, UI box
	$( "#date_filters input[type='date']" ).datepicker({
		showButtonPanel: true,
		dateFormat: 'yy-mm-dd'
	});

	// Redirect URL from form submission, so URL is pretty
	$('#date_filters').on('submit',function(e){
		var $form = $(this),
		date_from = $form.find('#date_from').val(),
		date_to = $form.find('#date_to').val();

		window.location = base_url + date_from + "/" + date_to;

		e.preventDefault();
	});

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