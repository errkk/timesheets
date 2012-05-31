
(function(){




	var dropbox = document.getElementById("dropbox"),
	$target	= $(dropbox),
	url_dump = '/gs/dump';



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
		label = document.getElementById("droplabel");

		if( 'text/xml' !== file.type ){
			label.innerHTML = 'Please drag the XML file from Grindstone';
			$target.removeClass('over').removeClass('dropped');
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

			  	var $list = $('#list').html('');
			  	$(data).each(function(i,item){
						var $li = $('<li>');
						$list.append( $li.html( item['name'] + ' ' + item['total'] ) ); 
			  	});
			  	label.innerHTML = "Your Tasks";

			  },
			  error: function(data){
			  	console.log('error');
			  }
			});
		}

		// begin the read operation
		reader.readAsDataURL(file);

		
	}



}());