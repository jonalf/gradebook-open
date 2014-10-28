var loadStudent = function() {
    
    $.post("/studentload",{},
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       var name = c['first'] + ' ' + c['last'];

	       heading = document.querySelectorAll('#sname')[0];
	       heading.innerText = "Grades for: " + name;
	   });

    loadGrades();
}

var loadGrades = function() {

        $.post("/studentgradeload",{},
           function( data, status ) {
	       var c = eval("(" + data + ")" );	       
	       s = '';
	       for  ( classn in c ) {
		   s+= '<h3>' + classn + '</h3>';
		   
		   for (type in c[ classn ]) {
		       if (c[ classn ][type].length > 0 ) {
 			   s+= '<h4>' + type + '</h4>';
			   s+= '<table class="report"><tr class="report1"><th>name</th><th>max</th><th>earned</th></tr>'
			   for (var i=0; i <  c[classn][type].length; i++ ) {
			       
			       if ( i%2 == 0 ) {
				   s+= '<tr class="report2">'; 
			       }
			       else {
				   s+= '<tr class="report1">'; 
			       }
			       s+= '<td>' + c[classn][type][i]['name'] + '</td>';
			       s+= '<td>' + c[classn][type][i]['max'] + '</td>';
			       s+= '<td>' + c[classn][type][i]['points'] + '</td></tr>';
			   }
			   s+= '</table>';
		       }
		   }
	       }

	       jumbo = document.querySelectorAll('#gradetables')[0];
	       	       
	       jumbo.innerHTML += s;
	   });    
}



