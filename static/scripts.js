var M_ATTENDANCE = 0;
var M_ARRANGE = 1;
var M_STUDENT = 2;
var M_ASSIGNMENT = 3;
var M_GRADES = 4;
var M_PARTICIPATION = 5

var selectedTerm = '';
var currentClass;
var currentStudent = null;
var arrangeSelected = false;
var selectedStudent;
var studentList;
var availableStudentList;
var assignmentTypes = null
var addRemove = false
var gradeOptions = []
var rows
var cols


//CLASS SELECTION FUNCTIONS
function loadselect(term) {
    selectedTerm = term;
    $.post("/loadselect",{},
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       var currentClasses = getClassList(c[selectedTerm], '')
	       $("#selection").html( currentClasses );

	       var oldClasses = '';
	       for (var i=0; i<c['terms'].length; i++) {
		   var term = c['terms'][i];
		   if (term != selectedTerm && term != 'terms') 
		       oldClasses+= getClassList( c[term], term )
	       }
	       $("#selection2").html( oldClasses );
           });
}

function loadSelectMenu(term) {
    selectedTerm = term;
    $.post("/loadselect",{},
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       var html = ''
	       var currentClasses = c[selectedTerm]
	       var classNames = getClassList2( c[selectedTerm], '' )
	       for ( var i=0; i < classNames.length; i++ ) {	       
		   html+= '<li><a href="/classview?classname=' + 
		       classNames[i] + '&term=' + selectedTerm + 
		       '">' + classNames[i] + '</a></li>'
	       }
	       var oldClasses = []
	       for (var i=0; i<c['terms'].length; i++) {
		   var t = c['terms'][i];
		   if (t != selectedTerm && t != 'terms') 
		       oldClasses.push(getClassList2( c[t], t ))
	       }
	       for (var i=0; i < oldClasses.length; i++) {
		   html+='<hr>'
		   for (var j=0; j < oldClasses[i].length; j++) {
		       oldClass = oldClasses[i][j].split(' ')
//		       html+= "<li><a onclick=\"loadclass('" + 
//		       oldClass[1] + "', '" + oldClass[0] + "', 0)\">"+ 
		       html+= '<li><a href="/classview?classname=' +
			   oldClass[1] + '&term=' + oldClass[0] +'">' +
			   oldClasses[i][j] + '</a></li>'
		   }
	       }
	       $('#selectmenu').html(html)
           });
}

function getClassList( classes, term ) {
    
    var text = ''
    var classNames = getClassList2( classes, term )
    for ( var i=0; i < classNames.length; i++ ) {
	text+= '<option>' + classNames[i] + '</option>';
    }
    return text;
}

function getClassList2( classes, term ) {
    
    var classNames = new Array();
    for ( var i=0; i < classes.length; i++ ) {
	classNames[i] = classes[i][0] + "-" + 
	    classes[i][1] + "-" + 
	    classes[i][2];
	if ( term != '' )
	    classNames[i] = term + ' ' + classNames[i];
    }
    classNames.sort();
    return classNames
} 
//===== END CLASS SELECTION FUNCTIONS =======


//LOAD FUNCTIONS FOR ALL STUDENT TABLE VIEWS
function loadclass( clsname, term, mode ) {
    selectedTerm = term;
    var sizeSet = true;
    loadSelectMenu( term )

    $.post("/loadclass", { classname : clsname, term : selectedTerm },
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       if ( !c )
		   return;
	       s = c["students"];
	       currentClass = clsname;
	       assignmentTypes = Object.keys(c['assignments'])
	       gradeOptions = c['options']
	       var numStudents = s.length;
	       var tmp = '<div class="row">'
	       tmp+= '<div class="col-md-10">'
	       var dbRows = c["rows"];
	       var dbCols = c["cols"];
           
	       if ( c["seated"] == 0 ) {
		   rows = Math.ceil( Math.sqrt( numStudents ));
		   cols = rows;
		   if ( numStudents < cols * cols  &&
			cols * ( rows - 1) >= numStudents ) {
		       rows = rows - 1;
		   }
		   tmp += getClassTable(s);
	       }
	       else {
		   rows = dbRows;
		   cols = dbCols;
		   tmp+= getClassTableSeated(s);
	       }
	       tmp+= '</div><div class="col-md-2"><div id="iface"></div></div></div>'
	       $('#content').empty();
	       $('#content').html( tmp );

	       $("#help_button").remove();
	       $('.message').remove()
	       $(".active").removeClass("active");
	       $("#classdropdown").addClass("active")
	       $('#nav_report').html('Reports <b class="caret">')

	       if ( mode == M_ARRANGE ) {
		   var buttons = '<button id="action_button"  class="btn btn-info btn-block" onclick="newSize()">Resize</button><hr><button class="btn btn-info btn-block" onclick="showPics()">Show Pictures</button>';
		   $('#iface').html(buttons);
		   $("#cterm").append('<button onclick="loadhelp(1)" id="help_button" class="btn btn-warning btn-xs">?</button>');
		   $('#nav_class').html('Arrange <b class="caret">')
	       }
	       else if ( mode == M_STUDENT ) {
		   var buttons = '<button id="action_button" class="btn btn-info btn-block" onclick="addStudent()">Add Student</button><hr><button class="btn btn-info btn-block" onclick="showPics()">Show Pictures</button></div>';
		   $("#iface").html(buttons);
		   $("#cterm").append('<button class="btn btn-warning btn-xs" onclick="loadhelp(2)" id="help_button">?</button>');
		   $('#nav_class').html('Student <b class="caret">')
	       }
	       else if ( mode == M_PARTICIPATION ) {
		   var buttons = '<button class="btn btn-info btn-block" onclick="pickRandom()">Random Student</button><hr><button class="btn btn-info btn-block" onclick="pickWeighted()">Weighted</button></div>';
		   $("#iface").html(buttons);
		   $("#cterm").append('<button class="btn btn-warning btn-xs" onclick="loadhelp(5)" id="help_button">?</button>');

		   $(".jumbotron").append('<h3 style="color: red;" class="message">Participation does not currently factor into grades. Currently, selecing "Weighted" will pick a random student but will be more likely to pick someone with a low participation total</h3>')

		   setStudentList(c['students'])
		   $('#nav_class').html('Participation <b class="caret">')
	       }
	       else if ( mode == M_ATTENDANCE ) {
		   var iface = '<button id="action_button" class="btn btn-info btn-block" onclick="saveAttendance()">Save Attendance</button><hr>';
		   iface+= '<input type="text" id="datepick" class="form-control" value="pick date"><hr><button class="btn btn-info btn-block" onclick="showPics()">Show Pictures</button></div>';
		   $("#iface").html(iface);
		   $("#datepick").datepick({showTrigger:"#calImg",
					    dateFormat:"m-d-yyyy",
					    onSelect:seeDaysAttendance});
		   seeDaysAttendance();
		   $("#cterm").append('<button class="btn btn-warning btn-xs" onclick="loadhelp(0)" id="help_button">?</button>');
		   $('#nav_class').html('Attendance <b class="caret">')
	       }
	       else if ( mode == M_ASSIGNMENT ) {
		   var html = '<div class="form-group"><input type="text" class="form-control input-sm" value="Assignment Name" id="aname">'
		   html+= '<input class="form-control input-sm" type="text" pattern="[0-9]*" value="Max Points" id="amax">'
		   html+= '<input type="text" class="form-control input-sm" pattern="[0-9]*" value="Default Points" id="adefault"><br>'
		   html+= loadAssignmentTypes( Object.keys(c['assignments']), 'radio')
		   html+= '<br><button class="btn btn-info btn-block" id="action_buton" onclick="saveGrades()">Save Grades</button><br><button class="btn btn-warning btn-block" id="adelete" onclick="deleteAssignment()">Delete Assignment</button></div><hr>'
		   html+= '<select class="form-control" id="aselection"></select><br><button class="btn btn-info btn-block" id="apick" onclick="changeAssignment()">Change Assignment</button><br></div>'
		   $("#iface").html(html);
		   $("#cterm").append('<button class="btn btn-warning btn-xs" onclick="loadhelp(3)" id="help_button">?</button>');
		   $('#nav_class').html('Assignment <b class="caret">')
		   getAssignments();
	       }
	       else if ( mode == M_GRADES ) {
		   var html = '<form class="form-horizontal"><div class="col-sm-12">Weights:</div>'
		   html+= loadAssignmentTypes( Object.keys(c['assignments']), 'weights', c)
		   html+= '</div></form>'
		   html+= '<button class="btn btn-info btn-block" onclick="changeWeights()">Change Weights</button><br><button class="btn btn-info btn-block" onclick="setGradeOptions()">More Options</button></div>'
		   $("#iface").html(html);
		   $("#cterm").append('<button class="btn btn-warning btn-xs" onclick="loadhelp(4)" id="help_button">?</button>');
		   $('#nav_class').html('Grades <b class="caret">')
	       }
	       setClickAction( mode, c['weights'] );
           });
    if ( mode == M_GRADES )
        showGrades();
    if ( mode != M_PARTICIPATION ) {
	studentList = null
	availableStudentList = null
    }
}

function loadAssignmentTypes( atypes, amode, c ) {
    var html = ''
    for (var i=0; i < atypes.length; i++) {
	atname = atypes[i];
	
	if ( amode == 'radio' ) {
	    html+= '<input type="radio" id="a' + atname + 
	'" name="atype" value="' + atname + '" checked>' +
	atname + '<br>'
	}
	
	else if ( amode == 'weights' ) {
	    html+= '<div class="form-group"><label for="' + atname + 'weight" class="col-sm-5 control-label">' + atname + '</label><div class="col-sm-7"><input class="form-control" id="' + atname + 'weight" type="text" pattern="[0-9]*" value ="' + c['weights'][atname] + '" size="3"></div></div>'
	}
    }
    return html
}

function setalert( id ) {
    
    var target = $( "#" + id);
    
    if ( target.css("color") == "rgb(51, 51, 51)" )
        target.addClass("redalert");
    
    else if ( target.css("color") == "rgb(255, 0, 0)" ) {
        target.removeClass("redalert");
        target.addClass("orangealert");
    }
    else if ( target.css("color") == "rgb(255, 165, 0)" ) {
        target.removeClass("orangealert");
        target.addClass("greenalert");
    }
    else if ( target.css("color") == "rgb(0, 128, 0)" ) {
        target.removeClass("greenalert");
        target.addClass("bluealert");
    }
    else
        target.removeClass("bluealert");
}

function loadhelp( mode ) {
    var helptext = "";
    if ( mode == M_ATTENDANCE )
        helptext = 'In attendance mode clicking on a student will cycle through 4 different attendance marks.\n\nRed: Absent\nOrange: Late\nGreen: Excused Absence\nBlue: Excused Lateness\n\nClicking "Save Attendance" will write the attendance data to the server. Selecting a different date will load the attendance data from that date';
    else if ( mode == M_ARRANGE )
        helptext = 'In arrange mode clicking on 2 consecutive students will swap their positions. This will also work with empty spaces. You can resize the class grid from 1x1 to 10x10. Setting a size that cuts off a row or column that contains students will make those students inaccesible (they can be retrieved by making the size larger).';
    else if ( mode == M_STUDENT )
        helptext = "In student mode clicking on a student will bring up a box where you can see and edit the student's contact/personal, attendace and grade information. You can also remove the student from the class, transfer the student to a different class or add a new student";
    else if ( mode == M_ASSIGNMENT )
        helptext = "In assignment mode you enter an assignment name, the maximum number of points and select the type of assignment (currently there are only Work, Test and Project categories). Then provide a grade for each student and click save grades to write the data to the server. Entering 'e', 'E', or '-1' will result in an excused assignment that will not count to the student's grade. Leaving a student grade blank will result in a grade of 0";
    else if ( mode == M_GRADES )
        helptext = "In grades mode each student's current grade will be calculated and displayed under the student's name. You can change the weights for each assignment types. Ideally, the total of all three weights should be 1.0";
    else if ( mode == M_PARTICIPATION )
        helptext = 'Participation mode'
    alert(helptext);
}

function getClassTable( students ) {
    
    var numStudents = students.length;
    var cs = 0;
    var text = '<table id="student_table">\n';
    var emptyID = -1;
    
    for ( var r=0; r < rows; r++ ) {
        
        text+= '<tr>'
        for ( var c=0; c < cols; c++ ) {
            
            if ( cs < numStudents ) {
                var cid = students[cs].id
                text+= '<td><div class="student" data-r="' + r +
                '" data-c="' + c + '" id="' + cid + '">'
                if ( students[cs].nick != "" )
                    text+= students[cs].nick + "<br>";
                text+= students[cs].first + "<br>" +
                students[cs].last + "<br></div></td>\n";
                $.post("/setseat", { classname:currentClass,term:selectedTerm, sid:cid, row:r, col:c });
                cs++;
            }
            else {
                text+= '<td><div class="student" data-r="' + r +
                '" data-c="' + c + '" id="' + emptyID +
                '"></div></td>\n';
                emptyID--;
            }
        }
        text+= '</tr>\n'
    }
    text+= '</table>'
    $.post("/seated",{classname:currentClass, term:selectedTerm, seated:1, rows:rows, cols:cols});
    return text;
}

function getClassTableSeated( students ) {
    var numStudents = students.length;
    var text = '<table id="student_table">\n';
    var emptyID = -1;
    
    for ( var r=0; r < rows; r++ ) {
        
        text+= '<tr>'
        for ( var c=0; c < cols; c++ ) {
            
            var s = findStudentBySeat( r, c, students );
            if ( s != null ) {
                var cid = s.id
                text+= '<td class="student" data-r="' + r + '" data-c="' + c + '" id="' + cid + '">'
                if ( s.nick != "" )
                    text+= s.nick + "<br>";
                text+= s.first + "<br>" + s.last + "<br></td>\n";
            }
            else {
                text+= '<td class="student" data-r="' + r + '" data-c="' + c + '" id="' + emptyID + '"></td>\n';
                emptyID--;
            }
        }
        text+= '</tr>\n'
    }
    text+= '</table>'
    return text;
}

function findStudentBySeat( r, c, students ) {
    
    for (var s=0; s < students.length; s++)
        if ( students[s]["row"] == r &&
            students[s]["col"] == c ) {
            return students[s];
        }
    return null;
}

function setClickAction( mode, weights ) {
    
    var actiontext = ""
    
    $(".student").each( function() {
        if ( mode == M_ATTENDANCE )
            actiontext = "setalert(" + this.id + ")";
        else if ( mode == M_ARRANGE )
            actiontext = "reseat(" + this.id + ")";
        else if ( mode == M_STUDENT )
            actiontext = "studentInfo(" + this.id + ")";
        else if ( mode == M_ASSIGNMENT && parseInt(this.id) >= 1000 )
            $(this).append('<br><input type="text" pattern="[0-9]*" size="3" id="grade">');
        else if (mode == M_PARTICIPATION && parseInt(this.id) >= 1000) {
	    var html = $(this).html()
	    var upbutton='<button class="votebutton" onclick="upvote(' + this.id + ')"> + </button>'
	    var downbutton='<button class="votebutton" onclick="downvote(' + this.id + ')"> - </button>'
	    html = '<div class="downcount">0</div>' +
		'<div class="upcount">0</div>' + 
		html + downbutton + upbutton;
//	    console.log( $(this).html() )
            $(this).html(html);	    
	}
        $(this).attr("onclick", actiontext);
    });
}

function showPics() {
    if ( $('img').length == 0 ) {
        $('.student_pic').remove();
        
        $.post('/validip', {},
               function(data, status) {
               var c = eval("(" + data + ")" );
               if ( c ) {
		   $(".student").each( function() {
                       if ( this.id > 0 ) {
                           img = $('<img class="student_pic">');
                           img.attr('src', '/static/studentpics/' + this.id + '.jpg');
                           img.attr('width', '115');
                           $(this).append(img);
                       }
                   });
               }
		   else
		       $('#temp').append('<br>Pictures can only be accessed while on the school network.');
               });
    }
    else
        $('.student_pic').remove();
}

function clearModal() {
    currentStudent = null
    $('.redalert').removeClass('redalert')
    $('.modal-title').empty()
    $('.modal-body').empty()
    $('.mbutton').remove()
    $('#mainmodal').modal('hide')
}

function overlay(clearStudent) {
    var v = $("#overlay").css("visibility");
    if ( v == "hidden" ) {
        $("#overlay").css("visibility", "visible");
        $("#overlay").height( $(document).height());
    }
    else {
        $("#overlay").css("visibility", "hidden");
        $("#modalbox").removeClass("");
        if ( clearStudent ) {
            currentStudent = null;
            $("#viewmid").remove();
        }
    }
}
//===== END GERNAL LOAD FUNCTIONS===========


//REPORTS FUNCTIONS

function loadreports( clsname, term ) {
    var html = "<h2>Please select the type of report you would like to see</h2>"
    html+= "<select id=\"rtype\">"
    html+= "<option value=\"r_all_attendance\">Todays Attendance (all classes)</option>"
    html+= "<option value=\"r_attendance\">Attendance Totals</option>"
    html+= "<option value=\"r_ogrades\">Overall Grades</option>"
    html+= "</select><br>"
    html+= "<button onclick=\"viewReport()\">Get Report</button>"
    
    $("#iface").remove();
    $("#help_button").remove();
    $('.message').remove()
    $('.button-warning').remove()
    $("#student_table").html( html );
    $("#classdropdown").removeClass("active")
    $('#nav_class').html('Classview <b class="caret">')
    $("#reportdropdown").addClass("active");
}

function viewReport() {

    var rtype = $("#rtype").val();
    var html = "<button onclick=\"loadreports()\">Back to Reports</button><br>";    
    $("#report").remove();
    $("#student_table").html(html);

    if ( rtype == "r_attendance" ) {
	generateAttendanceTotalReport();
    }
    else if ( rtype == "r_all_attendance" ) {
	var day = new Date();
	var dateString = (day.getMonth() + 1) + "-" + day.getDate() + "-" + day.getFullYear();		
	generateAttendanceReport2( dateString );
    }
    else if ( rtype == "r_ogrades") {
	generateFullGradesReport();
    }
}

function generateFullGradesReport() {

    $('.active').removeClass('active')
    $('#nav_class').html('Classview <b class="caret">')
    $('#nav_report').html('Grades <b class="caret">')
    $('#reportdropdown').addClass('active')
    $('.message').remove()
    $('#iface').remove()
    $('.btn-warning').remove()

    $.post("/loadclass", { classname : currentClass,term:selectedTerm}, 
	   function( data, status ) {
	       var c = eval("(" + data + ")" );
	       if ( !c )
		   return;
	       var workTotal = 0;
	       var testTotal = 0;
	       var projectTotal = 0;
	       var gradeTotal = 0;
	       var rGradeTotal = 0;
	       var html= "<div id=\"report\"><table><tr><td><h2>Class Grades</h2><br>";
	       var table = "<table class=\"report\"><tr class=\"report1\"><th>Last Name</th><th>First Name</th>"

	       gradeOptions = c['options']
	       atypes = Object.keys(c['assignments'])
	       for (var i=0; i < atypes.length; i++)
		   table+= '<th>' + atypes[i] + '</th>'
	       table+= '<th>Grade</th><th>Rounded Grade</th></tr>';


	       cs = c['students'];
	       cs.sort( compareStudentNames );

	       var aTotals = {}
	       for (var i=0; i < atypes.length; i++)
		   aTotals[ atypes[i] ] = 0

	       for (var i = 0; i < c['students'].length; i++) {
		   s = c['students'][i];
		   if ( i%2 == 1 )
		       table+= "<tr class=\"report1\">";
		   else
		       table+= "<tr class=\"report2\">";
		   table+= "<td>"+ s['last'] +
		       "</td><td>"+s['first'] +"</td>";
		   
		   assignments = s['assignments']		   
		   var g = 0
		   for (var at=0; at < atypes.length; at++) {
		       var a = computeGradePart(assignments[atypes[at]], atypes[at])
		       g+= a * c['weights'][atypes[at]]
		       aTotals[ atypes[at] ]+= a
		       
		       table+='<td>' + a.toFixed(2) + '</td>'
		   }
		   var rg = getRoundedGrade( g );		   
		   gradeTotal+= g;
		   rGradeTotal+= rg;

		   table+= "<td>" + 
		       g.toFixed(2) + "</td>";
		   table+= "<td>" + 
		       rg + "</td></tr>";
	       }
	       gradeTotal = gradeTotal / c['students'].length;
	       rGradeTotal = rGradeTotal / c['students'].length;

	       table+= "<tr><td colspan=\"2\">Averages</td>" 
	       for (var i=0; i < atypes.length; i++) {

		   aTotals[atypes[i]] = aTotals[atypes[i]] /
		       c['students'].length
		   table+= '<td>' + aTotals[atypes[i]].toFixed(2) + "</td>"
	       }
	       table+= '<td>' + gradeTotal.toFixed(2) + "</td><td>" +
		   rGradeTotal.toFixed(2) + "</td></tr>"
	       table+= "</table></td></tr>";

	       html += table;
	       for (var i=0; i < atypes.length; i++) {
		   atype = atypes[i]
		   var atable = getGradeTable( c['students'],
					       c['assignments'][atype], atype)
		   html+= '<tr><td><h2>' + atype + ' Grades</h2><br>'
		   html+= atable
		   html+= '</td></tr>'
	       }	       
	       html+= '</div>';
	       $("#student_table").html(html);
	       $("#temp").remove()
	       $("td").addClass("report");
	       $("th").addClass("report");
	   });
}

function getGradeTable( students, assignments, type ) {
    var anames = new Array();
    var ascores = new Array( assignments.length );
    var acounts = new Array( assignments.length );
    for (var i=0; i < ascores.length; i++)
	ascores[i] = 0;

    for (var i=0; i < assignments.length; i++) {
	anames[i] = assignments[i]['name'];
	acounts[i] = 0;
    }

    var table = "<table class=\"report\"><tr class=\"report1\"><th>Last Name</th><th>First Name</th>";
    for (var i=0; i < anames.length; i++)
	table+= "<th>" + anames[i] + "</th>";
    table+= "</tr>"

    for (var i=0; i < students.length; i++) {
	var info = getStudentWorkRow(students[i], anames, type, i);
	table+= info['text'];
	for ( var g=0; g < ascores.length; g++) {
	    p = info['grades'][g];
	    if ( p != -1 ) {
		ascores[g] += p;
		acounts[g]+= 1;
	    }
	}
    }
    table+= "<tr><td colspan=\"2\">Averages</td>";
    for (var i=0; i < ascores.length; i++) {
	ascores[i] = ascores[i] / acounts[i];
	table+= "<td>" + ascores[i].toFixed(2) + "</td>";
    }
    table+= "</tr></table>";
    return table;
}

function getStudentWorkRow(student, anames, type, mod) {
    var scores = new Array( anames.length );
    if ( mod % 2 == 1 )
	var trow = "<tr class=\"report1\">";
    else 
	var trow = "<tr class=\"report2\">";

    trow+= "<td>" + student['last'] + "</td><td>" + 
	student['first'] + "</td>";
    for (var i=0; i < anames.length; i++ ) {
	for (var j=0; j< student['assignments'][type].length; j++)
	    if ( anames[i] == student['assignments'][type][j]['name']) {
		p = student['assignments'][type][j]['points'];
		if ( p != -1 )
		    trow+= "<td>" + p + "</td>";
		else
		    trow+= "<td>E</td>";
		scores[i] = parseFloat(student['assignments'][type][j]['points']);
	    }
    }
    trow+= "</tr>";
    var x = { text:trow, grades:scores };
    return x;
}

function getRoundedGrade( grade ) {
    if ( grade >= 90 )
	return Math.round(grade);
    else if ( grade >= 87.5 )
	return 88;
    else if ( grade >= 82.5 )
	return 85;
    else if ( grade >= 77.5 )
	return 80;
    else if ( grade >= 72.5 )
	return 75;
    else if ( grade >= 67.5 )
	return 70;
    else if (grade >= 62.5 )
	return 65;
    else if (grade >= 57.5 )
	return 60;
    else
	return 0;
}

function computeGradePart(grades, type, weight){
    var points = 0
    var max = 0

    if ( type == 'tests' && grades.length > 0 ) {
	var lowtotal = grades[0]['points']
	var lowtmax = grades[0]['max']	
	var lowavg = grades[0]['points'] / lowtmax	
	var lowapoints = lowtotal
	var lowamax = lowtmax
    }

    for (var i=0; i < grades.length; i++) {
	if ( grades[i]['points'] != -1 ) {
	    var p = grades[i]['points'];
	    var m = grades[i]['max'];
	    points+= p
	    max+= m
	    
	    if ( type == 'tests' ) {
		if ( p < lowtotal ) {
		    lowtotal = p
		    lowtmax = m
		}
		if ( p/m < lowavg ) {
		    lowavg = p/m
		    lowapoints = p
		    lowamax = m
		}
	    }
	}
    }
    
    if ( type == 'tests' ) {
	if ( gradeOptions.indexOf('drop-avg') != -1 ) {
	    points-= lowapoints
	    max-= lowamax
	}
	else if ( gradeOptions.indexOf('drop-total') != -1 ) {
	    points-= lowtotal
	    max-= lowtmax
	}
    }

    var grade = points / max;
    if ( isNaN(grade) )
	grade = 0;

    if ( weight == null ) {
	return grade * 100
    }
    else {
	return grade * weight;
    }
}
/*
function getGradeAverage( grades ) {
    var total = 0;
    var max = 0;
    for( var i=0; i < grades.length; i++ ) {
	p = parseFloat( grades[i]['points'] );
	if ( p != -1 ) {
	    total+= p;
	    max += parseFloat( grades[i]['max'] );
	}
    }
    var avg = total / max;
    if ( isNaN(avg) )
	avg = 0;
    return avg * 100;
}
*/
function generateAttendanceTotalReport() {
    $('.active').removeClass('active')
    $('#nav_class').html('Classview <b class="caret">')
    $('#nav_report').html('Attendance Totals <b class="caret">')
    $('#reportdropdown').addClass('active')
    $('.message').remove()
    $('#iface').remove()
    $('.btn-warning').remove()

    $.post("/loadclass", { classname : currentClass,term:selectedTerm}, 
	   function( data, status ) {
	       var c = eval("(" + data + ")" );
	       if ( !c )
		   return;
	       var html = generateAttendanceTotalTable( c['students'],
						    currentClass);
	       $("#student_table").html(html);
	       $("#temp").remove()
	       $("td").addClass("report");
	       $("th").addClass("report");
	       $("#datepick").datepick({showTrigger:"#calImg",
					dateFormat:"m-d-yyyy"});
	   });
}


function generateAttendanceReport2( dateString ) {

    $('.active').removeClass('active')
    $('#reportdropdown').addClass('active')
    $('#nav_class').html('Classview <b class="caret">')
    $('#nav_report').html('Daily Attendance <b class="caret">')
    $('.message').remove()
    $('#iface').remove()
    $('.btn-warning').remove()

    if ( !dateString ) {
	dateString = $("#datepick").val();
	$("#report").remove();
	$(".report").remove();
    }

    if ( dateString == 1 ) {
	var day = new Date();
	dateString = (day.getMonth() + 1) + "-" + day.getDate() + "-" + day.getFullYear();		
    }

    $.post("/loadselect", {},
	   function( data, status ) {
	       var c = eval("(" + data + ")" );
	       c = c[selectedTerm];      
	       classes = new Array();
	       var html = "<div id=\"report\"><input type=\"text\" id=\"datepick\" value=\"pick date\"><button onclick=\"generateAttendanceReport2()\">View Day</button><br><table>";	       

	       
	       for ( var i=0; i < c.length; i++ ) {
		   var cls = c[i][0] +"-"+ c[i][1] +"-"+ c[i][2];
		   classes[i] = cls;
	       }
	       classes.sort();

	       for (var i=0; i < classes.length; i++)
		   html+= '<tr><td><div id="att_' + classes[i] +
		   '"></div></td></tr>';
	       
	       $("#temp").remove()
	       $("#student_table").html(html);

	       for (var i=0; i < classes.length; i++) {
		   
		   $.post("/loadclass", { classname : classes[i],
					  term:selectedTerm }, 
			  function( data, status ) {
			      var d = eval("(" + data + ")" );
			      if ( !d )
				  return;
		   	      
			      var cls = d['code'] +'-'+ d['section'] +
				  '-'+ d['period'];
			      var html = generateAttendanceTable(dateString, d['students'], cls);
			      html+= "</table></div>";	       
			      $('#att_' + cls).append( html );
			      $("td").addClass("report");
			      $("th").addClass("report");
			  });
	       }
	       $("#student_table").append("</table>");
	       $("#datepick").datepick({showTrigger:"#calImg",
					dateFormat:"m-d-yyyy"});
	   });
}


function generateAttendanceTable( dateString, students, cls ) {

    var table = "<h2>" + cls + " Attendance for " + dateString + "</h2><br>";
    table+= "<table class=\"report\"><tr class=\"report1\"><th>Last Name</th><th>First Name</th><th>Attendance</th></tr>"

    students.sort( compareStudentNames );

    for ( var i=0; i < students.length; i++ ) {
	s = students[i];
	if ( i % 2 == 1 )
	    table+= "<tr class=\"report1\"><td>";
	else
	    table+= "<tr class=\"report2\"><td>";
	table+= s['last'] +"</td><td>"+ s['first'] +"</td>";
	if ( s['absent'].indexOf( dateString ) != -1 ||
	     s['excused'].indexOf( dateString )  != -1)
	    table+= "<td>Absent</td></tr>";
	else if ( s['late'].indexOf( dateString ) != -1 ||
		  s['exlate'].indexOf( dateString )  != -1)
	    table+= "<td>Late</td></tr>";
	else
	    table+= "<td></td></tr>";
    }
    table+= "</table></div>";
    return table;
}

function generateAttendanceTotalTable( students, cls ) {

    var table = "<h2>Attendance Totals</h2>";
    table+= "<table class=\"report\"><tr class=\"report1\"><th>Last Name</th><th>First Name</th><th>Absent</th><th>Late</th><th>Excused Absences</th><th>Excused Latnesses</th></tr>"

    students.sort( compareStudentNames );

    for ( var i=0; i < students.length; i++ ) {
	s = students[i];
	if ( i % 2 == 1 )
	    table+= "<tr class=\"report1\"><td>";
	else 
	    table+= "<tr class=\"report2\"><td>";
	
	ab = s['absent'].length
	if ( ab == 0)
	    ab = '-'
	ea = s['excused'].length
	if ( ea == 0)
	    ea = '-'
	la = s['late'].length
	if ( la == 0)
	    la = '-'
	el = s['exlate'].length
	if ( el == 0)
	    el = '-'

	table+= s['last'] +"</td><td>"+ s['first'] +"</td>";
	table+= '<td>' + ab + '</td>' +
	    '<td>' + la  + '</td>' +
	    '<td>' + ea + '</td>' +
	    '<td>' + el + '</td></tr>';
    }
    table+= "</table></div>";
    return table;
}

function compareStudentNames(s1, s2) {
    if ( s1['last'] < s2['last'] )
	return -1;
    else if ( s1['last'] > s2['last'] )
	return 1;
    else if ( s1['first'] < s2['first'] )
	return -1;
    else if ( s1['first'] > s2['first'] )
	return 1;
    else 
	return 0;
}

//==== END REPORTS FUNCTIONS ===============


//BACKUP FUNCTION
function loadbackups(term) {
    var html = "<h3>Download a Backup CSV (for use in an external spreadsheet program)</h3><a href=\"getbackupcsv?classname=" + currentClass + "&term=" + selectedTerm + "\"><button>Download Backup CSV</button></a><br>";
    html+= "<h3>Download a Backup CSV of ALL CLASSES (for use in an external spreadsheet program)</h3><a href=\"getallbackupcsv?term=" + selectedTerm + "\"><button>Download All Class Backup CSV</button></a><br>";
    html+= "<h3>Download a Backup File (for use with this website via the restore tool below)</h3><a href=\"getbackup?classname=" + currentClass + "&term=" + selectedTerm + "\"><button>Download Class Backup</button></a><br>";
    html+= "<h3>Download a Backup File for ALL CLASSES (for use with this website via the restore all tool below)</h3><a href=\"getallbackup?term=" + selectedTerm +"\"><button>Download All Class Backup</button></a><br>";
    html+= "<h3>Restore from a previous backup</h3>";
    html+= '<form action="/backuprestore" method="post" enctype="multipart/form-data">';
    html+= "Backup File: <input type=\"file\" name=\"backupfile\">";
    html+= "<input type=\"submit\" name=\"Restore\" value=\"Restore\"></form><br>";
    html+= "<h3>Restore ALL CLASSES from a previous backup</h3>";
    html+= '<form action="/backupallrestore" method="post" enctype="multipart/form-data">';
    html+= "Backup File: <input type=\"file\" name=\"backupfile\">";
    html+= "<input type=\"submit\" name=\"Restore All\" value=\"Restore All\"></form>";

    $("#temp").remove();
    $("#help_button").remove();
    $("#student_table").empty();
    $("#student_table").append(html);
    $("a.active").removeClass("active");
    $("#nav_bac").addClass("active");
}


//ATTENDANCE MODE FUNCTIONS
function saveAttendance() {
    var absences = new Array();
    var latenesses = new Array();
    var excuses = new Array();
    var exlates = new Array();
    
    if ( isValidDate($('#datepick').val()) )
	var dateStamp = $('#datepick').val();
    else {
	var d = new Date();
	var dateStamp = d.getMonth()+1 + "-" + d.getDate() + "-" + d.getFullYear();
    }
    
    $(".redalert").each(
        function() {
            absences.push( $(this).attr("id") );
        });
    $(".orangealert").each(
        function() {
            latenesses.push( $(this).attr("id") );
        });
    $(".greenalert").each(
        function() {
            excuses.push( $(this).attr("id") );
        });
    $(".bluealert").each(
        function() {
            exlates.push( $(this).attr("id") );
        });
    $.post("/saveattendance", { classname : currentClass,
				term:selectedTerm,
				date : dateStamp,
				absent : absences.join("_"), 
				late : latenesses.join("_"),
				excused : excuses.join("_"),
				exlates : exlates.join("_")} );  
}

function seeDaysAttendance( day ) {
    if ( day == null )
        day = new Date();
    else
        day = day[0];
    dateString = (day.getMonth() + 1) + "-" + day.getDate() + "-" + day.getFullYear();
    
    clearAttendance();
    
    $.post("/gettoday", {classname:currentClass, 
			 term:selectedTerm,
			 date:dateString},
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       
	       for (s in c['absent'])
		   $("#" + c['absent'][s]).addClass("redalert");
	       for (s in c['late'])
		   $("#" + c['late'][s]).addClass("orangealert");
	       for (s in c['excused'])
		   $("#" + c['excused'][s]).addClass("greenalert");
	       for (s in c['exlate'])
		   $("#" + c['exlate'][s]).addClass("bluealert");
           });
}

function clearAttendance() {
    $(".redalert").removeClass("redalert");
    $(".orangealert").removeClass("orangealert");
    $(".greenalert").removeClass("greenalert");
    $(".bluealert").removeClass("bluealert");
}

function formatDateArray( a ) {
    for (var i=0; i < a.length; i++)
        a[i] = (a[i].getMonth() + 1) + "-" + a[i].getDate() + "-" + a[i].getFullYear();
    return a;
}

function isValidDate( s ) {
    d = s.split('-');
    for (var i=0; i < d.length; i++)
	d[i] = parseInt(d[i]);
    return d.length == 3 && 
	d[0] >= 1 && d[0] <= 12 &&
	d[1] >= 1 && d[1] <= 31 &&
	d[2] >= 1000 && d[2] <= 3000;
	
}
//===== END ATTENDANCE MODE FUNCTIONS =======


//PARTICIPATION MODE FUNCTIONS
function upvote( id ) {
    console.log( id );
    var upcount = parseInt($('#'+id+' .upcount').text())
    upcount++
    console.log( upcount );
    $('#'+id+' .upcount').text(upcount)
}

function downvote( id ) {
    var downcount = parseInt($('#'+id+' .downcount').text())
    downcount++
    console.log( downcount )
    $('#'+id+' .downcount').text(downcount)
}

function setStudentList( students ) {

    studentList = {}
    availableStudentList = []
    for (var i=0; i < students.length; i++) {
	studentList[students[i]['id']] =  0
	availableStudentList[i] = students[i]['id']
    }
}

function resetAvailableStudents( ids ) {
    availableStudentList = []
    for (var i=0; i < ids.length; i++)
	availableStudentList[i] = ids[i]    
}

function getParticipationTotal() {
    var total = 0
    for (var id in studentList ) {
	var p = parseFloat( $('#' + id + ' .upcount').text() )
	if ( p == 1 )
	    total+= .75
	else if ( p != 0 )
	    total+= 1.0 / p
	else
	    total+= 1
    }
    return total
}

function pickWeighted() {
    $(".bluealert").removeClass("bluealert");
    var total = getParticipationTotal()
    var r = Math.random() * total
    var t = 0
    for (var id in studentList ) {
	var p = parseFloat( $('#' + id + ' .upcount').text() )
	if ( p == 1 )
	    t+= .75
	else if ( p != 0 )
	    t+= 1.0 / p
	else
	    t+= 1
	if ( r <= t ) {	    
	    $('#' + id).addClass('bluealert')
	    return id
	}
    }    
}

function pickRandom() {
    $(".bluealert").removeClass("bluealert");    
    if ( availableStudentList.length == 0 )
	resetAvailableStudents( Object.keys(studentList) )

    var r = Math.floor( Math.random() * 
			availableStudentList.length )
    var s = availableStudentList.splice(r, 1)[0]    
    $('#' + s).addClass('bluealert')
    console.log(s)
}

//===== END PARTICIPATION MODE FUNCTIONS =======


//ARRANGE MODE FUNCTIONS
function reseat( id ) {
    if ( !arrangeSelected ) {
        arrangeSelected = true;
        selectedStudent = id;
        $("#" + id).addClass("redalert");
    }
    
    else {
        var target1 = $( "#" + id);
        var target2 = $( "#" + selectedStudent);
        
        var sname = target2.html();
        target2.html( target1.html());
        target2.attr("id", id);
        target2.attr("onclick", "reseat(" + id + ")");
        
        target1.html( sname );
        target1.attr("id", selectedStudent);
        target1.attr("onclick", "reseat(" + selectedStudent + ")");
        
        target2.removeClass("redalert");
        arrangeSelected = false;
        
        $.post("/reseat", { classname:currentClass,
			    term:selectedTerm,
			    id1 : id,
			    row1 : target2.attr("data-r"),
			    col1 : target2.attr("data-c"),
			    id2 : selectedStudent,
			    row2 : target1.attr("data-r"),
			    col2 : target1.attr("data-c") } )
    }
}

function newSize() {
       
    var html = '<form class="form-horizontal">'

    html+= '<div class="form-group"><label for="rows" class="col-sm-4" control-label>Rows</label><div class="col-sm-8"><select id="rows" class="form-control">'
    for (var i=1; i <= 10; i++)
        html+= '<option value="' + i + '">' + i + '</option>'
    html+= '</select></div></div>'

    html+= '<div class="form-group"><label for="cols" class="col-sm-4" control-label>Cols</label><div class="col-sm-8"><select id="cols" class="form-control">'
    for (var i=1; i <= 10; i++)
        html+= '<option value="' + i + '">' + i + '</option>'
    html+= '</select></div></div></form>'
    
    var button = '<button type="button" class="mbutton btn btn-info" onclick="resize()">Resize</button>'
    $(".modal-body").html(html);

    $('#rows').val(rows)
    $('#cols').val(cols)

    $('.modal-title').text('Resize Class Grid')
    $('.mbutton').remove()
    $('.modal-footer').append(button)
    $('#mainmodal').modal('show')
}

function resize() {
    rows = $("#rows").attr("value");
    cols = $("#cols").attr("value");
    sizeChanged = true;
    
    $.post("/loadclass", { classname : currentClass, term:selectedTerm,
			   rows : rows, cols : cols },
           function( data, status ) {
	       var s = eval("(" + data + ")" );
	       $("#student_table").empty();
	       if ( s["seated"] == 0 )
		   $("#student_table").append( getClassTable(s["students"]) );
	       else
		   $("#student_table").append( getClassTableSeated(s["students"]));
	       setClickAction( M_ARRANGE );
           });
    clearModal()
}

//====== END ARRANGE MODE FUNCTIONS =======


//STUDENT MODE FUNCTIONS
function addStudent() {
    if ( $("#-1").length == 0 ) {
        var message = "<h3>There is no spot for a new student, resize the class and then add the student.</h3>";
        $("#temp").append( message );
    }
    else {
        var html = "<table border=\"0\">"
        html+= "<tr><td>First Name:</td><td><input type=\"text\" id=\"first\"></td></tr>";
        html+= "<tr><td>Last Name:</td><td><input type=\"text\" id=\"last\"></td></tr>";
        html+= "<tr><td>Nickname:</td><td><input type=\"text\" id=\"nick\"></td></tr>";
        html+= '<tr><td>OSIS:</td><td><input type="text" pattern="[0-9]*" id="id"></td></tr>'
        html+= '<tr><td>ID:</td><td><input type="text" pattern="[0-9]*" id="stuyid"></td></tr>'
        html+= '<tr><td>HR:</td><td><input type="text" pattern="[0-9]*" id="hr"></td></tr>'
        html+= "<tr><td>Email:</td><td><input type=\"text\" id=\"email\"></td></tr></table>";

        var buttons = '<button class="btn btn-info mbutton" onclick="newStudent()">Add Student</button>'
        
	$('.modal-title').text('Add a New Student')
        $('.modal-body').html(html);
	$('.mbutton').remove()
	$('.modal-footer').append(buttons)
	$('#mainmodal').modal('show')
    }
}

function newStudent() {
    var first = $("#first").val();
    var last = $("#last").val();
    var nick = $("#nick").val();
    var id = $("#id").val();
    var email = $("#email").val();
    var stuyid = $("#stuyid").val();
    var hr = $("#hr").val();
    
    var r = $("#-1").attr("data-r");
    var c = $("#-1").attr("data-c");

    var proceed = true
    var missing = '<p style="color:red">The following required fields are missing: '
    if ( first == '' ) {
	proceed = false;
	missing+= 'First Name '
    }
    if ( last == '' ) {
	proceed = false;
	missing+= 'Last Name '
    }
    if ( id == '' ) {
	proceed = false;
	missing+= 'OSIS '
    }

    if ( proceed ) {
	$.post("/addstudent", {classname:currentClass,term:selectedTerm,
				first:first, last:last, nick:nick, 
				sid:id, email:email,
				row:r, col:c, stuyid:stuyid, hr:hr},
               function( data, status ) {
	       loadclass( currentClass, selectedTerm, M_STUDENT);
		   $('#mainmodal').modal('hide')
               });    
    }
    
    else {
	missing+= '</p>'
	$('.modal-body').append(missing)
    }
}

function studentInfo(id) {
    var html = '';
    if ( parseInt(id) >= 1000 ) {
        $('#mainmodal').modal('show')
	$('.mbutton').remove()
        
        $.post("/getinfo", { classname : currentClass, term:selectedTerm, sid : id  },
               function( data, status ) {
		   var c = eval("(" + data + ")" )[0];
		   currentStudent = c;
		   
		   $('.modal-title').text(c['first'] + ' ' + c['last'])
		   html+= '<div class="row">'
		   html+= '<div class="col-sm-4"><button type="button" class="btn btn-info btn-stack" onclick="infoView()">Student Information</button></div>'
		   html+= '<div class="col-sm-4"><button type="button" class="btn btn-info btn-stack" onclick="attendanceView()">Student Attendance</button></div>'
		   html+= '<div class="col-sm-4"><button type="button" class="btn btn-info btn-stack" onclick="workView()">Student Work</button></div></div>'
		   html+= '<br><div class="row"><div class="col-sm-6"><button type="button" class="btn btn-warning btn-stack" onclick="removeStudent()">Remove Student</button></div>'
		   html+= '<div class="col-sm-6"><button type="button" class="btn btn-warning btn-stack" onclick="transferStudent()">Transfer Student</button></div></div></div>'

		   $('.modal-body').html(html);
               });          
    }
}

function removeStudent() {
    var html = '<b>Are you sure you want to remove this student from your class? This action cannot be undone!<b>' 
    var buttons = '<button class="btn btn-warning mbutton" type="button" onclick="removeStudentConfirm()">Remove Student</button>'

    $('.modal-body').html(html);
    $('.modal-body').addClass('redalert')
    $('.modal-footer').append(buttons)
}

function removeStudentConfirm() {
    $.post("/removestudent", {classname:currentClass, term:selectedTerm,
			      sid: currentStudent['id'] },
           function( data, status ) {
	       loadclass( currentClass, selectedTerm, M_STUDENT);
	       clearModal()
           });
}

function transferStudent() {
    
    $.post("/loadselect", {},
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       c = c[selectedTerm];
	       var menu = "<select id=\"newclass\">"
	       menu+= getClassList(c, '');
	       menu+= "</select>";
	       
	       var html = "Please select one of your other classes to transfer this student to:<br>" + menu;
	       var buttons = '<button class="btn btn-warning mbutton" onclick="transfer()">Transfer</button>'
	       $('.modal-body').html(html);
	       $('.modal-footer').append(buttons)
           });
}

function transfer() {
    var targetClass = $("#newclass").val();
    $.post("/transferstudent",{classname:currentClass,term:selectedTerm,
			       sid: currentStudent['id'],
			       targetclass:targetClass },
           function( data, status ) {
	       if ( data == "false" ) {
		   var html = '<b>The target class does not have enough room for a new student, please change the seating size for that class and try again.<b>'
		   $('.mbutton').remove()
		   $('.modal-body').html(html)
	       }
	       else {
		   loadclass( currentClass, selectedTerm, M_STUDENT);
		   clearModal()
	       }
           });
}


//INFO VIEW FUNCTIONS
function infoView() {
    var html = "<table border=\"0\">"
    html+= "<tr><td>Nickname:</td><td>" + currentStudent['nick'] + "</td></tr>";
    html+= "<tr><td>OSIS:</td><td>" + currentStudent['id'] + "</td></tr>";
    html+= "<tr><td>ID:</td><td>" + currentStudent['stuyid'] + "</td></tr>";
    html+= "<tr><td>HR:</td><td>" + currentStudent['hr'] + "</td></tr>";
    html+= "<tr><td>Email:</td><td>" + currentStudent['email'] + "</td></tr>";
    html+= '</table>'
    
    var button = '<button id="backbutton" class="mbutton btn btn-default" onclick="studentInfo(' + currentStudent['id'] + ')">Back</button><button class="btn btn-info mbutton" onclick="editInfo()">Edit</button>'
    
    $('.mbutton').remove()
    $('.modal-body').html(html)
    $('.modal-footer').append(button)
}

function editInfo() {
    var html = "<table border=\"0\">"
    html+= "<tr><td>Nickname:</td><td><input type=\"text\" id=\"nick\" value=\"" + currentStudent['nick'] + "\"></td></tr>";
    html+= '<tr><td>OSIS:</td><td><input type="text" pattern="[0-9]*" id="id" value="' + currentStudent['id'] + '"></td></tr>';
    html+= '<tr><td>ID:</td><td><input type="text" pattern="[0-9]*" id="stuyid" value="' + currentStudent['stuyid'] + '"></td></tr>';
    html+= "<tr><td>HR:</td><td><input type=\"text\" id=\"hr\" value=\"" + currentStudent['hr'] + "\"></td></tr>";
    html+= "<tr><td>Email:</td><td><input type=\"text\" id=\"email\" value=\"" + currentStudent['email'] + "\"></td></tr>";
    html+= '</table><br><br>'

    var buttons='<button class="btn btn-default mbutton" id="backbutton" onclick="infoView()">Back</button><button class="btn btn-info mbutton" onclick="saveInfo()">Save</button>'
    
    $('.modal-body').html(html)
    $('.mbutton').remove()    
    $('.modal-footer').append(buttons)
}

function saveInfo() {
    $.post("/saveinfo", {classname:currentClass, term:selectedTerm,
			 sid:currentStudent['id'],
			 nick: $("#nick").val(), id:$("#id").val(),
			 email: $("#email").val(), hr: $("#hr").val(),
			 stuyid: $("#stuyid").val()},
           function(data, status) {
	       var c = eval("(" + data + ")" )[0];
	       currentStudent = c;
	       infoView();
           });
}
//END INFO VIEW FUNCTIONS


//ATTENDANCE VIEW FUNCTIONS
function attendanceView() {
    var calendars = '<div class="row">'
    calendars += '<div class="col-sm-6 col-xs-12"><b>Absences ' + currentStudent['absent'].length + '</b><div id="abscal"></div></div>'
    calendars += '<div class="col-sm-6 col-xs-12"><b>Excused Absences ' + currentStudent['excused'].length + '</b><div id="exccal"></div></div></div>'
    calendars += '<br><div class="row"><div class="col-sm-6 col-xs-12"><b>Latenesses ' + currentStudent['late'].length + '</b><div id="latcal"></div></div>'
    calendars += '<div class="col-sm-6 col-xs-12"><b>Excused Latenesses ' + currentStudent['exlate'].length + '</b><div id="exlcal"></div></div></div>'

    $('.modal-body').html(calendars)

    var buttons = '<button class="btn btn-default mbutton" id="backbutton" onclick="studentInfo(' + currentStudent['id'] + ')">Back</button><button class="btn btn-info mbutton" type="button" onclick="changeAttendance(' + currentStudent["id"] + ')">Change Attendance</button>'
 
    $('.modal-footer').append(buttons);
    
    $("#abscal").datepick({"dateFormat":"m-d-yyyy",
                          "multiSelect":20});
    $("#latcal").datepick({"dateFormat":"m-d-yyyy",
                          "multiSelect":20});
    $("#exccal").datepick({"dateFormat":"m-d-yyyy",
                          "multiSelect":20});
    $("#exlcal").datepick({"dateFormat":"m-d-yyyy",
                          "multiSelect":20});
    $("#abscal").datepick("setDate", currentStudent["absent"]);
    $("#latcal").datepick("setDate", currentStudent["late"]);
    $("#exccal").datepick("setDate", currentStudent["excused"]);
    $("#exlcal").datepick("setDate", currentStudent["exlate"]);
}

function changeAttendance( id ) {
    
    abs = formatDateArray( $("#abscal").datepick("getDate") );
    lat = formatDateArray( $("#latcal").datepick("getDate") );
    exc = formatDateArray( $("#exccal").datepick("getDate") );
    exl = formatDateArray( $("#exlcal").datepick("getDate") );
    
    $.post("/changeattendance", {classname:currentClass, 
				 term:selectedTerm, sid:id,
				 absent:abs.join("_"),
				 late:lat.join("_"),
				 excused:exc.join("_"),
				 exlate:exl.join("_")});
    studentInfo( currentStudent['id'] );
}
//END ATTENDANCE VIEW FUNCTONS


//WORK VIEW FUNCTIONS
function workView() {
    var gradeInfo = "<table border=\"0\">";

    var atypes = Object.keys(currentStudent['assignments'])
    for (var i=0; i < atypes.length; i++) {
	gradeInfo+= getWorkRow( atypes[i] );
    }
    gradeInfo += "</table>";    
    var buttons = '<button class="btn btn-default mbutton" id="backbutton" onclick="studentInfo(' + currentStudent['id'] + ')">Back</button>';
    
    $('.modal-body').html( gradeInfo )    
    $('.mbutton').remove()
    $('.modal-footer').append(buttons)
}

function getWorkRow( type ) {
    var word = type[0].toUpperCase() + type.slice(1);
    var gradeInfo = "<tr><td>" + word + "</td>";
    var totalPoints = 0;
    var maxPoints = 0;

    for (var i=0; i<currentStudent['assignments'][type].length; i++) {
	p = parseFloat(currentStudent['assignments'][type][i]['points'])
	if ( p != -1 ) {
            totalPoints+= p;
            maxPoints+= parseFloat(currentStudent['assignments'][type][i]['max']);
	}
    }
    gradeInfo += "<td>" + totalPoints + "/" + maxPoints + "</td><td>";
    if ( maxPoints == 0 )
        gradeInfo+= "-</td>";
    else
        gradeInfo+= (totalPoints/maxPoints * 100).toFixed(2) + "%</td>"
    gradeInfo += "<td><button class=\"btn btn-default\" onclick=\"fullWorkReport('" + type + "', " + totalPoints + ", " + maxPoints + ")\">Full View</button></td></tr>";
    
    return gradeInfo;
}

function fullWorkReport( type, total, max ) {
    var word = type[0].toUpperCase() + type.slice(1);
    var html= "<center><h4>" + word + " summary: " + total + "/" + max + " ";
    if ( max == 0 )
        html+= "-</h4></center>";
    else
        html+= (total/max * 100).toFixed(2) + "%</h4></center>";
    
    var missing = new Array();
    var excused = new Array();
    var workTable = '<br><center><h4>All Assignments</h4></center>'
    var numAssignments = currentStudent['assignments'][type].length;

    for (var ca=0; ca < numAssignments; ca++) {
        var name = currentStudent['assignments'][type][ca]['name'];
        var points = currentStudent['assignments'][type][ca]['points'];
        var maxPoints = parseFloat(currentStudent['assignments'][type][ca]['max']);
        workTable+= "<button class=\"btn btn-default\" onclick=\"gradeChangeView('" + ca + "', '" + type + "', '" + currentStudent['id'] + "')\">"+  name +" ";
        if ( points == 0 )
            missing.push( name );
	if ( points == -1 ) {
	    excused.push( name );
	    workTable+= "E</button>";
	}
	else
	    workTable+= points + "/" + maxPoints + "</button>";
    }
    
    if ( missing.length == 0 )
        html+= "Missing: -"
    else
        html+= "Missing: " + missing;
    if ( excused.length == 0 )
        html+= "<br>Excused: -"
    else
        html+= "<br>Excused: " + excused;

    html+= "<br>" + workTable
    
    var buttons = '<button class="btn btn-default mbutton" id="backbutton" onclick="workView()">Back</button>'
    $('.mbutton').remove()
    $('.modal-body').html( html );
    $('.modal-footer').append(buttons);
}

function gradeChangeView(ca, type, id) {
    var name = currentStudent['assignments'][type][ca]['name'];
    var points = currentStudent['assignments'][type][ca]['points'];
    var maxPoints = parseFloat(currentStudent['assignments'][type][ca]['max']);
    
    var html = "Assignment: <b>" + name + "</b> Max Points: <b>" + maxPoints + "</b><br>";
    html+= "Current Grade: <b>";
    if  ( points != -1 )
	html+= points;
    else 
	html+= "E";
    html+= '</b> Change to: <input type="text" pattern="[0-9]*" size="3" id="newgrade">'
    var buttons= "<button class=\"btn btn-default mbutton\" id=\"backbutton\" onclick=\"workView()\">Back</button><button class=\"btn btn-info mbutton\" onclick=\"changeGrade('" + ca + "', '" + type + "', '" + id + "')\">Change Grade</button>";
    
    $('.mbutton').remove()
    $('.modal-body').html( html );
    $('.modal-footer').append(buttons);
}

function changeGrade(ca, type, id) {
    var ng = $("#newgrade").val();
    var newGrade = parseFloat(ng);
    if ( ng == 'e' || ng == 'E' )
	newGrade = -1;
    else if ( isNaN( newGrade ) )
        newGrade = 0;
    currentStudent['assignments'][type][ca]['points'] = newGrade;
    $.post("/changegrade",{classname:currentClass, term:selectedTerm,
			   atype: type,
			   grades:JSON.stringify(currentStudent['assignments'][type]), sid:id},
           function( data, status) {
	       var c = eval("(" + data + ")" )[0];
	       currentStudent = c;
	       gradeChangeView(ca, type, id);
           });
}
//END WORK VIEW FUNCTIONS
//====== END STUDENT MODE FUNCTIONS ===========


//ASSIGNMENT MODE FUNCTIONS
function saveGrades() {
    var grades = {};
    var defaultg = $('#adefault').val()
    if ( defaultg == 'e' || defaultg == 'E' )
	defaultg = -1
    else if ( isNaN( parseFloat(defaultg) ) )
	defaultg = 0
    else
	defaultg = parseFloat( defaultg )
	      
    $(".student").each(
        function() {
	    if ( parseInt(this.id) >= 1000 ) {
                var g = $(this).find("input").val();
		if ( g == 'e' || g == 'E' )
		    g = -1
                else if ( isNaN(parseFloat(g)) )
                    g = defaultg;
                else
                    g = parseFloat(g);
                grades[this.id] = g;
            }
        });
    $.post("/savegrades", { classname:currentClass,
			    term:selectedTerm,
			    grades:JSON.stringify(grades),
			    aname:$("#aname").val(),
			    atype:$("[type=radio]:checked").val(), 
			    points:parseFloat($("#amax").val())},
           function(data, status) {
               loadclass( currentClass, selectedTerm, M_GRADES);
           });
}

function getAssignments() {
    $.post("/getassignments",{classname:currentClass,term:selectedTerm},
	   function(data, status) {
	       var c = eval("(" + data + ")" );
	       var html = '';
	       for(var i=0; i < c.length; i++)
		   html+= '<option>' + c[i] + '</option>';
	       $('#aselection').html(html);
	   });
}

function changeAssignment() {
    clearAttendance();
    $.post("/getassignment", { classname:currentClass,term:selectedTerm,
			       aname : $('#aselection').val() },
	   function(data, status) {
	       var c = eval("(" + data + ")" );

	       $('#aname').val( c['name'] );
	       $('#amax').val( c['max'] );
	       $('#adefault').val( '0' )
	       var t = 'a' + c['type'];
	       $('#' + t).prop('checked', true);

	       for(var i=0; i < c['grades'].length; i++) {
		   s = c['grades'][i]
		   if (s['grade'] != -1)
		       $('#' + s['id']).find('input').val(s['grade']);
		   else {
		       $('#' + s['id']).find('input').val('E');
		       $('#' + s['id']).addClass("greenalert");
		   }
		   if (s['grade'] == 0)
		       $('#' + s['id']).addClass("redalert");
	       }
	   });
}

function deleteAssignment() {
    var assignment = $('#aname').val()
    var atype = $('[type=radio]:checked').val()
    var html = 'Are you sure you want to remove this assignment? Doing so will delete it from the database. This action is cannot be reversed.'
    var button = '<button type="button" class="mbutton btn btn-info" onclick="deleteAssignmentConfirm()">Delete Assignment</button>'

    $('.modal-title').html('Remove ' + atype + ': ' + assignment + '?')
    $('.modal-body').html(html);
    $('.modal-body').addClass('redalert')
    $('.modal-footer').append(button)
    $('#mainmodal').modal('show')    
}

function deleteAssignmentConfirm() {    

    var ids = []
    $(".student").each(
        function() {
	    if ( parseInt(this.id) >= 1000 ) {
		ids.push( this.id )
	    }
	});
    $.post("/deletegrades", { classname:currentClass,
			      term:selectedTerm,
			      ids:JSON.stringify(ids),
			      aname:$("#aname").val(),
			      atype:$("[type=radio]:checked").val() }, 	   
           function(data, status) {
               loadclass( currentClass, selectedTerm, M_GRADES);
           });
    clearModal()
}
//====== END ASSIGNMENT MODE FUNCTIONS ========


//GRADE MODE FUNCTIONS
function showGrades() {

    $('.redalert').removeClass('redalert')
    $('.orangealert').removeClass('orangealert')
    
    $.post("/loadclass", { classname : currentClass,term:selectedTerm },
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       students = c['students'];
               gradeOptions = c['options']
	       
	       $(".grade").remove();
           
	       for (var i=0; i < students.length; i++) {
		   var grade = computeGrade( students[i], c['weights'] );
		   $("#" + students[i]['id']).append("<div class=\"grade\"><br>"
                                             + grade.toFixed(2) +
                                             "</div>");
		   if ( grade < 65 )
		       $("#" + students[i]['id']).addClass('redalert')
		   else if ( grade < 75 )
		       $("#" + students[i]['id']).addClass('orangealert')
	       }
           });
}

function computeGrade( student, weights ) {

    var grade = 0;
    
    var atypes = Object.keys( student['assignments'] )
    for (var i=0; i < atypes.length; i++) {
	var a = atypes[i]
	grade+= computeGradePart(student['assignments'][a], a, weights[a])
    }
    grade = grade * 100;
    return grade;
}

function changeWeights() {

    var weights = {}
    for (var i=0; i < assignmentTypes.length; i++) {
	a = assignmentTypes[i];
	var w = parseFloat( $('#' + a + 'weight').val() )
	if ( isNaN(w) ) 
	    weights[a] = 0
	else
	    weights[a] = w
    }
    
    $.post("/changeweights", {classname:currentClass,
			      term:selectedTerm,
			      weights: JSON.stringify(weights)},
           function(data, status) {
               showGrades();
           });
}

function setGradeOptions() {
    var html = 'Drop the lowest test grade by average: '
    html+= '<button onclick="saveGradeOption(\'drop-avg\')"'
    if ( gradeOptions.indexOf( 'drop-avg' ) == -1 ) 
	html+= 'class="btn btn-default">Inactive'
    else
	html+= 'class="btn btn-success">Active'
    html+= '</button><br><br>'

    html+= 'Drop the lowest test grade by total points: '
    html+= '<button onclick="saveGradeOption(\'drop-total\')"'
    if ( gradeOptions.indexOf( 'drop-total' ) == -1 ) 
	html+= 'class="btn btn-default">Inactive</button>'
    else
	html+= 'class="btn btn-success">Active</button>'

    $('.modal-body').html( html )
    $('.modal-title').html('Grade Options')
    $('#mainmodal').modal('show')
}

function saveGradeOption( opt ) {

    $.post("/savegradeoptions", {classname:currentClass,
				term:selectedTerm,
				option: opt },
	   function(data, status) {
	       $('#mainmodal').modal('hide')
               showGrades();
           });   
}


//====== END GRADE MODE FUNCTIONS ============
