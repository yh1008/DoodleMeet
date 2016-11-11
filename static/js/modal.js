$(".ratingsbutton").click(function(){
	functioncalled();
});

function functioncalled(){
	console.log(myaid);
	$.getJSON($SCRIPT_ROOT + "/find_activitygear",{query:4}).done(function(data){
	modal.style.display = "block";
});
}


