var M_ATTENDANCE = 0;
var M_ARRANGE = 1;
var M_STUDENT = 2;
var M_ASSIGNMENT = 3;
var M_GRADES = 4;

var currentClass;
var currentStudent = null;
var arrangeSelected = false;
var selectedStudent;
var addRemove = false;
var rows;
var cols;


//CLASS SELECTION FUNCTIONS
function loadselect() {
    $.post("/loadselect",{},
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       $("#selection").html( getClassList(c) );
           });
}

function getClassList( classes ) {
    
    var text = "";
    for ( var i=0; i < classes.length; i++ ) {
        text+= "<option>" + classes[i][0] + "-" + classes[i][1] + "-" + classes[i][2] + "</option>\n";
    }
    return text;
} 
//===== END CLASS SELECTION FUNCTIONS =======


//LOAD FUNCTIONS FOR ALL STUDENT TABLE VIEWS
function loadclass( clsname, mode ) {
    var sizeSet = true;
    $.post("/loadclass", { classname : clsname },
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       if ( !c )
		   return;
	       s = c["students"];
	       currentClass = clsname;
	       var numStudents = s.length;
	       var tmp = null;
	       var dbRows = c["rows"];
	       var dbCols = c["cols"];
           
	       if ( c["seated"] == 0 ) {
		   rows = Math.ceil( Math.sqrt( numStudents ));
		   cols = rows;
		   if ( numStudents < cols * cols  &&
               cols * ( rows - 1) >= numStudents ) {
           rows = rows - 1;
		   }
		   tmp = getClassTable(s);
	       }
	       else {
		   rows = dbRows;
		   cols = dbCols;
		   tmp = getClassTableSeated(s);
	       }
	       $("#student_table").empty();
	       $("#student_table").append( $(tmp) );
	       $("#action_button").remove();
	       $("#datepick").remove();
	       $("#temp").remove();
	       $("#help_button").remove();
	       if ( mode == M_ARRANGE ) {
		   var buttons = "<div id=\"temp\"><button id='action_button' onclick=\"newSize()\">Resize</button><br><button onclick=\"showPics()\">Show Pictures</button></div>";
		   $("#student_table").after(buttons);
		   $("h1").append('<button onclick="loadhelp(1)" id="help_button">?</button>');
	       }
	       else if ( mode == M_STUDENT ) {
		   var buttons = "<div id=\"temp\"><button id='action_button' onclick=\"addStudent()\">Add Student</button></div>";
		   $("#student_table").after(buttons);
		   $("h1").append('<button onclick="loadhelp(2)" id="help_button">?</button>');
	       }
	       else if ( mode == M_ATTENDANCE ) {
           var iface = "<div id=\"temp\"><br><button id='action_button' onclick=\"saveAttendance()\">Save Attendance</button><br>";
		   iface+= "<input type=\"text\" id=\"datepick\" value=\"pick date\"><br><button onclick=\"showPics()\">Show Pictures</button></div>";
		   $("#student_table").after(iface);
		   $("#datepick").datepick({showTrigger:"#calImg",
                                   dateFormat:"m-d-yyyy",
                                   onSelect:seeDaysAttendance});
		   seeDaysAttendance();
           $("h1").append('<button onclick="loadhelp(0)" id="help_button">?</button>');
	       }
	       else if ( mode == M_ASSIGNMENT ) {
		   var html = "<div id=\"temp\"><input type=\"text\" value=\"Assignment Name\" id=\"aname\"><br>"
		   html+= "<input type=\"text\" value=\"Max Points\" id=\"amax\"><br>"
		   html+= "<input type=\"radio\" name=\"atype\" value=\"work\" checked>Work<br>"
		   html+= "<input type=\"radio\" name=\"atype\" value=\"tests\">Test<br>"
		   html+= "<input type=\"radio\" name=\"atype\" value=\"projects\">Project<br>"
		   html+= "<button id=\"action_buton\" onclick=\"saveGrades()\">Save Grades</button></div>"
		   $("#student_table").after(html);
		   $("h1").append('<button onclick="loadhelp(3)" id="help_button">?</button>');
	       }
	       else if ( mode == M_GRADES ) {
		   var html = "<div id=\"temp\">Weights:<br><table border=\"0\">"
		   html+= "<tr><td>work:</td><td><input id=\"workweight\" type=\"text\" value =\"" + c['weights']['work'] + "\" size=\"3\"></td></tr>";
		   html+= "<tr><td>tests:</td><td><input id=\"testweight\" type=\"text\" value =\"" + c['weights']['tests'] + "\" size=\"3\"></td></tr>";
		   html+= "<tr><td>projects:</td><td><input id=\"projectweight\" type=\"text\" value =\"" + c['weights']['projects'] + "\" size=\"3\"></td></tr></table>";
		   html+= "<button onclick=\"changeWeights()\">Change Weights</button></div>";
		   $("#student_table").after(html);
           $("h1").append('<button onclick="loadhelp(4)" id="help_button">?</button>');
	       }
	       setClickAction( mode, c['weights'] );
           });
    if ( mode == M_GRADES )
        showGrades();
}

function setalert( id ) {
    
    var target = $( "#" + id);
    
    if ( target.css("color") == "rgb(0, 0, 0)" )
        target.addClass("redalert");
    
    else if ( target.css("color") == "rgb(255, 0, 0)" ) {
        target.removeClass("redalert");
        target.addClass("orangealert");
    }
    else if ( target.css("color") == "rgb(255, 165, 0)" ) {
        target.removeClass("orangealert");
        target.addClass("greenalert");
    }
    else
        target.removeClass("greenalert");
}

function loadhelp( mode ) {
    var helptext = "";
    if ( mode == M_ATTENDANCE )
        helptext = 'In attendance mode clicking on a student will cycle through 4 different attendance marks.\n\nRed: Absent\nOrange: Late\nGreen: Excused\n\nClicking "Save Attendance" will write the attendance data to the server. Selecting a different date will load the attendance data from that date';
    else if ( mode == M_ARRANGE )
        helptext = 'In arrange mode clicking on 2 consecutive students will swap their positions. This will also work with empty spaces. You can resize the class grid from 1x1 to 10x10. Setting a size that cuts off a row or column that contains students will make those students inaccesible (they can be retrieved by making the size larger).';
    else if ( mode == M_STUDENT )
        helptext = "In student mode clicking on a student will bring up a box where you can see and edit the student's contact/personal, attendace and grade information. You can also remove the student from the class, transfer the student to a different class or add a new student";
    else if ( mode == M_ASSIGNMENT )
        helptext = "In assignment mode you enter an assignment name, the maximum number of points and select the type of assignment (currently there are only Work, Test and Project categories). Then provide a grade for each student and click save grades to write the data to the server. Entering 'e', 'E', or '-1' will result in an excused assignment that will not count to the student's grade. Leaving a student grade blank will result in a grade of 0";
    else if ( mode == M_GRADES )
        helptext = "In grades mode each student's current grade will be calculated and displayed under the student's name. You can change the weights for each assignment types. Ideally, the total of all three weights should be 1.0";
    alert(helptext);
}

function getClassTable( students ) {
    
    var numStudents = students.length;
    var cs = 0;
    var text = "";
    var emptyID = -1;
    
    for ( var r=0; r < rows; r++ ) {
        
        text+= "<tr>\n"
        for ( var c=0; c < cols; c++ ) {
            
            if ( cs < numStudents ) {
                var cid = students[cs].id
                text+= "<td><div class=\"student\" data-r=\"" + r +
                "\" data-c=\"" + c + "\" id=\"" + cid + "\">"
                if ( students[cs].nick != "" )
                    text+= students[cs].nick + "<br>";
                text+= students[cs].first + "<br>" +
                students[cs].last + "<br></div></td>\n";
                $.post("/setseat", { classname:currentClass,
                       sid:cid, row:r, col:c });
                cs++;
            }
            else {
                text+= "<td><div class=\"student\" data-r=\"" + r +
                "\" data-c=\"" + c + "\" id=\"" + emptyID +
                "\"></div></td>\n";
                emptyID--;
            }
        }
        text+= "</tr>\n"
    }
    $.post("/seated",{classname:currentClass, seated:1, rows:rows, cols:cols});
    return text;
}

function getClassTableSeated( students ) {
    var numStudents = students.length;
    var text = "";
    var emptyID = -1;
    
    for ( var r=0; r < rows; r++ ) {
        
        text+= "<tr>\n"
        for ( var c=0; c < cols; c++ ) {
            
            var s = findStudentBySeat( r, c, students );
            if ( s != null ) {
                var cid = s.id
                text+= "<td><div class=\"student\" data-r=\"" + r + "\" data-c=\"" + c + "\" id=\"" + cid + "\">"
                if ( s.nick != "" )
                    text+= s.nick + "<br>";
                text+= s.first + "<br>" + s.last + "<br></div></td>\n";
            }
            else {
                text+= "<td><div class=\"student\" data-r=\"" + r + "\" data-c=\"" + c + "\" id=\"" + emptyID + "\"></div></td>\n";
                emptyID--;
            }
        }
        text+= "</tr>\n"
    }
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
                       $(this).append("<br><input type=\"text\" size=\"3\" id=\"grade\">");
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

function loadreports( clsname ) {
    var html = "<h2>Please select the type of report you would like to see</h2>"
    html+= "<select id=\"rtype\">"
    html+= "<option value=\"r_attendance\">Attendance</option>"
    html+= "<option value=\"r_ogrades\">Overall Grades</option>"
    html+= "</select><br>"
    html+= "<button onclick=\"viewReport()\">Get Report</button>"
    
    $("#temp").remove();
    $("#help_button").remove();
    $("#student_table").html( html );
}

function viewReport() {

    var rtype = $("#rtype").val();
    var html = "<button onclick=\"loadreports()\">Back to Reports</button><br>";
    
    $("#report").remove();
    $("#student_table").html(html);

    if ( rtype == "r_attendance" ) {
	var day = new Date();
	var dateString = (day.getMonth() + 1) + "-" + day.getDate() + "-" + day.getFullYear();
	generateAttendanceReport( dateString );
    }
    else if ( rtype == "r_ogrades") {
	generateFullGradesReport();
    }
}

function generateFullGradesReport() {
    $.post("/loadclass", { classname : currentClass }, 
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
	       var table = "<table class=\"report\"><tr class=\"report1\"><th>Last Name</th><th>First Name</th><th>Work</th><th>Tests</th><th>Projects</th><th>Grade</th><th>Rounded Grade</th></tr>";
	       
	       for (var i = 0; i < c['students'].length; i++) {
		   s = c['students'][i];
		   if ( i%2 == 1 )
		       table+= "<tr class=\"report1\">";
		   else
		       table+= "<tr class=\"report2\">";
		   table+= "<td>"+ s['last'] +
		       "</td><td>"+s['first'] +"</td>";
		   
		   var w = getGradeAverage( s['work'] );
		   var t = getGradeAverage( s['tests'] );
		   var p = getGradeAverage( s['projects'] );
		   var g = w * c['weights']['work'] +
		       t * c['weights']['tests'] +
		       p * c['weights']['projects'];
		   var rg = getRoundedGrade( g );

		   workTotal+= w;
		   testTotal+= t;
		   projectTotal+= p;
		   gradeTotal+= g;
		   rGradeTotal+= rg;

		   table+= "<td>" +
		       w.toFixed(2) + "</td>";
		   table+= "<td>" + 
		       t.toFixed(2) + "</td>";
		   table+= "<td>" + 
		       p.toFixed(2) + "</td>";
		   table+= "<td>" + 
		       g.toFixed(2) + "</td>";
		   table+= "<td>" + 
		       rg + "</td></tr>";
	       }

	       workTotal = workTotal / c['students'].length;
	       testTotal = testTotal / c['students'].length;
	       projectTotal = projectTotal / c['students'].length;
	       gradeTotal = gradeTotal / c['students'].length;
	       rGradeTotal = rGradeTotal / c['students'].length;
	       table+= "<tr><td colspan=\"2\">Averages</td><td>" + 
		   workTotal.toFixed(2) + "</td><td>" +
		   testTotal.toFixed(2) + "</td><td>" + 
		   projectTotal.toFixed(2) + "</td><td>" + 
		   gradeTotal.toFixed(2) + "</td><td>" +
		   rGradeTotal.toFixed(2) + "</td></tr>"
	       table+= "</table></td></tr>";
	       html += table;
	       var table2 = getGradeTable( c['students'], 
					   c['work'], 'work');
	       var table3 = getGradeTable( c['students'], 
					   c['tests'], 'tests');
	       var table4 = getGradeTable( c['students'], 
					   c['projects'], 'projects');
	       html += "<tr><td><h2>Work Grades</h2><br>"
	       html+= table2;
	       html += "</td></tr><tr><td><h2>Test Grades</h2><br>"
	       html+= table3;
	       html += "</td></tr><tr><td><h2>Project Grades</h2><br>"
	       html+= table4 + "</td></tr></div>";
	       $("#student_table").append(html);
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
	for (var j=0; j< student[type].length; j++)
	    if ( anames[i] == student[type][j]['name'] ) {
		p = student[type][j]['points'];
		if ( p != -1 )
		    trow+= "<td>" + p + "</td>";
		else
		    trow+= "<td>E</td>";
		scores[i] = parseFloat(student[type][j]['points']);
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

function generateAttendanceReport( dateString ) {
    
    if ( !dateString ) {
	dateString = $("#datepick").val();
	$("#report").remove();
    }
	
    $.post("/loadclass", { classname : currentClass }, 
	   function( data, status ) {
	       var c = eval("(" + data + ")" );
	       if ( !c )
		   return;
		   var html = "<div id=\"report\"><h2>Attendance for " + dateString + 
		   "</h2><br>";
		   html+= "<input type=\"text\" id=\"datepick\" value=\"pick date\">";
		   html+= "<button onclick=\"generateAttendanceReport()\">View Day</button><br>"
		   
		   var table = "<table class=\"report\"><tr class=\"report1\"><th>Last Name</th><th>First Name</th><th>Attendance</th></tr>"
		   for ( var i=0; i < c['students'].length; i++ ) {
		       s = c['students'][i];
		       if ( i % 2 == 1 )
			   table+= "<tr class=\"report1\"><td>";
		       else
			   table+= "<tr class=\"report2\"><td>";
		       table+= s['last'] +"</td><td>"+ s['first'] +"</td>";
		       if ( s['absent'].indexOf( dateString ) != -1 ||
			    s['excused'].indexOf( dateString )  != -1)
			   table+= "<td>Absent</td></tr>";
		       else if ( s['late'].indexOf( dateString ) != -1 )
			   table+= "<td>Late</td></tr>";
		       else
			   table+= "<td></td></tr>";
		   }
	       table+= "</table></div>";
	       html+= table;
	       
	       $("#student_table").append(html);
	       $("td").addClass("report");
	       $("th").addClass("report");
	       $("#datepick").datepick({showTrigger:"#calImg",
					dateFormat:"m-d-yyyy"});
	   });
}
//==== END REPORTS FUNCTIONS ===============


//BACKUP FUNCTION
function loadbackups() {
    var html = "<h3>Download a Backup CSV (for use in an external spreadsheet program)</h3><a href=\"getbackupcsv?classname=" + currentClass + "\"><button>Download Backup CSV</button></a><br>";
    html+= "<h3>Download a Backup File (for use with this website via the restore tool below)</h3><a href=\"getbackup?classname=" + currentClass + "\"><button>Download Class Backup</button></a><br>";
    html+= "<h3>Restore from a previous backup</h3>";
    html+= "<form action=\"/backuprestore\" method=\"post\" enctype=\"multipart/form-data\">";
    html+= "Backup File: <input type=\"file\" name=\"backupfile\">";
    html+= "<input type=\"submit\" name=\"Restore\" value=\"Restore\"></form>";
    $("#temp").remove();
    $("#help_button").remove();
    $("#student_table").empty();
    $("#student_table").append(html);
}


//ATTENDANCE MODE FUNCTIONS
function saveAttendance() {
    var absences = new Array();
    var latenesses = new Array();
    var excuses = new Array();
    
    var d = new Date();
    var dateStamp = d.getMonth()+1 + "-" + d.getDate() + "-" + d.getFullYear();
    
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
    $.post("/saveattendance", { classname : currentClass,
           date : dateStamp,
           absent : absences.join("_"), 
           late : latenesses.join("_"),
           excused : excuses.join("_") } );  
}

function seeDaysAttendance( day ) {
    if ( day == null )
        day = new Date();
    else
        day = day[0];
    dateString = (day.getMonth() + 1) + "-" + day.getDate() + "-" + day.getFullYear();
    
    clearAttendance();
    
    $.post("/gettoday", {classname:currentClass, date:dateString},
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       
	       for (s in c['absent'])
		   $("#" + c['absent'][s]).addClass("redalert");
	       for (s in c['late'])
		   $("#" + c['late'][s]).addClass("orangealert");
	       for (s in c['excused'])
		   $("#" + c['excused'][s]).addClass("greenalert");
           });
}

function clearAttendance() {
    $(".redalert").removeClass("redalert");
    $(".orangealert").removeClass("orangealert");
    $(".greenalert").removeClass("greenalert");
}

function formatDateArray( a ) {
    for (var i=0; i < a.length; i++)
        a[i] = (a[i].getMonth() + 1) + "-" + a[i].getDate() + "-" + a[i].getFullYear();
    return a;
}
//===== END ATTENDANCE MODE FUNCTIONS =======


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
               id1 : id,
               row1 : target2.attr("data-r"),
               col1 : target2.attr("data-c"),
               id2 : selectedStudent,
               row2 : target1.attr("data-r"),
               col2 : target1.attr("data-c") } )
    }
}

function addStudent() {
    if ( $("#-1").length == 0 ) {
        var message = "<h3>There is no spot for a new student, resize the class and then add the student.</h3>";
        $("#temp").append( message );
    }
    else {
        overlay();
        var html = "<table border=\"0\">"
        html+= "<tr><td>First Name:</td><td><input type=\"text\" id=\"first\"></td></tr>";
        html+= "<tr><td>Last Name:</td><td><input type=\"text\" id=\"last\"></td></tr>";
        html+= "<tr><td>Nickname:</td><td><input type=\"text\" id=\"nick\"></td></tr>";
        html+= "<tr><td>OSIS:</td><td><input type=\"text\" id=\"id\"></td></tr>";
        html+= "<tr><td>ID:</td><td><input type=\"text\" id=\"stuyid\"></td></tr>";
        html+= "<tr><td>HR:</td><td><input type=\"text\" id=\"hr\"></td></tr>";
        html+= "<tr><td>Email:</td><td><input type=\"text\" id=\"email\"></td></tr>";
        html+= "</table><br><br><button onclick=\"newStudent()\">Add Student</button>";
        html+= "<hr style=\"width: 100%\"><button type=\"button\" onclick=\"overlay(true)\">Close</button>"
        $("#modalbox").removeClass();
        $("#modalbox").addClass("infobox");
        $("#modalbox").html(html);
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
    
    $.post("/addstudent", { classname:currentClass, first:first,
           last:last, nick:nick, sid:id, email:email,
           row:r, col:c, stuyid:stuyid, hr:hr},
           function( data, status ) {
	       loadclass( currentClass, M_STUDENT);
	       overlay(true);
           });    
}

function newSize() {
    overlay();
    getNewSize();
}

function getNewSize() {
    
    var html = "<table border=\"0\"><tr><td>Rows</td><td>Cols</td></tr>"
    
    html+= "<tr><td><select id=\"rows\">"
    for (var i=1; i <= 10; i++)
        html+= "<option value=\"" + i + "\">" + i + "</option>"
        
        html+= "</select></td><td><select id=\"cols\">"
        for (var i=1; i <= 10; i++)
            html+= "<option value=\"" + i + "\">" + i + "</option>"
            html+= "</select></td></tr></table><br><button onclick=\"resize()\">Resize</button><br>";
    html+= "<button onclick=\"overlay()\">Cancel</button>";
    $("#modalbox").html(html);
    $("#modalbox").addClass("resizebox");
}

function resize() {
    rows = $("#rows").attr("value");
    cols = $("#cols").attr("value");
    
    sizeChanged = true;
    
    $.post("/loadclass", { classname : currentClass, rows : rows, cols : cols },
           function( data, status ) {
	       var s = eval("(" + data + ")" );
	       $("#student_table").empty();
	       if ( s["seated"] == 0 )
		   $("#student_table").append( getClassTable(s["students"]) );
	       else
		   $("#student_table").append( getClassTableSeated(s["students"]));
	       setClickAction( M_ARRANGE );
           });
    
    overlay(-1);
}
//====== END ARRANGE MODE FUNCTIONS =======


//STUDENT MODE FUNCTIONS
function studentInfo(id) {
    var html = "";
    if ( parseInt(id) >= 1000 ) {
        if ( currentStudent == null )
            overlay();
        
        $.post("/getinfo", { classname : currentClass, sid : id  },
               function( data, status ) {
               var c = eval("(" + data + ")" )[0];
               currentStudent = c;
               html+= "<center><h2>" + c["first"] + "<br>";
               html+= c["last"] + "</h2></center><hr>";
               html+= "<div id=\"viewmid\">"
               html+= "<button type=\"button\" onclick=\"infoView()\">Student Information</button>";
               html+= "<button type=\"button\" onclick=\"attendanceView()\">Student Attendance</button>";
               html+= "<button type=\"button\" onclick=\"workView()\">Student Work</button>";
               html+= "<br><br><button type=\"button\" onclick=\"removeStudent()\">Remove Student</button>";
               html+= "<button type=\"button\" onclick=\"transferStudent()\">Transfer Student</button></div>";
               html+= "<hr style=\"width: 100%\"><button type=\"button\" onclick=\"overlay(true)\">Close</button>"
               $("#modalbox").removeClass();
               $("#modalbox").addClass("studentbox");
               $("#modalbox").html(html);
               });          
    }
}

function removeStudent() {
    var html = "<b>Are you sure you want to remove this student from your class? This action cannot be undone!<b><br><button type=\"button\" onclick=\"removeStudentConfirm()\">Remove Student</button>"
    $("#viewmid").html(html);
    $("#modalbox").addClass("redalert");
}

function removeStudentConfirm() {
    $.post("/removestudent", { classname:currentClass,
           sid: currentStudent['id'] },
           function( data, status ) {
	       loadclass( currentClass, M_STUDENT);
	       overlay(true);
           });
}

function transferStudent() {
    
    $.post("/loadselect", {},
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       var menu = "<select id=\"newclass\">"
	       menu+= getClassList(c);
	       menu+= "</select>";
	       
	       var html = "Please select one of your other classes to transfer this student to:<br>" + menu;
	       html+= "<button onclick=\"transfer()\">Transfer</button>";
	       $("#viewmid").html( html );
           });
}

function transfer() {
    var targetClass = $("#newclass").val();
    $.post("/transferstudent", { classname:currentClass,
           sid: currentStudent['id'],
           targetclass:targetClass },
           function( data, status ) {
	       if ( data == "false" ) {
		   var html = "<b>The target class does not have enough room for a new student, please change the seating size for that class and try again.<b>";
		   $("#viewmid").html(html);
	       }
	       else {
		   loadclass( currentClass, M_STUDENT);
		   overlay(true);
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
    html+= "</table><br><br><button onclick=\"editInfo()\">Edit</button>";
    
    $("#viewmid").html(html);
    var buttons = "<button id=\"backbutton\" onclick=\"studentInfo(" + currentStudent['id'] + ")\">Back</button>";
    
    $("#backbutton").remove();
    $("#modalbox").append(buttons);
    $("#modalbox").removeClass();
    $("#modalbox").addClass("infobox");
}

function editInfo() {
    var html = "<table border=\"0\">"
    html+= "<tr><td>Nickname:</td><td><input type=\"text\" id=\"nick\" value=\"" + currentStudent['nick'] + "\"></td></tr>";
    html+= "<tr><td>OSIS:</td><td><input type=\"text\" id=\"id\" value=\"" + currentStudent['id'] + "\"></td></tr>";
    html+= "<tr><td>ID:</td><td><input type=\"text\" id=\"stuyid\" value=\"" + currentStudent['stuyid'] + "\"></td></tr>";
    html+= "<tr><td>HR:</td><td><input type=\"text\" id=\"hr\" value=\"" + currentStudent['hr'] + "\"></td></tr>";
    html+= "<tr><td>Email:</td><td><input type=\"text\" id=\"email\" value=\"" + currentStudent['email'] + "\"></td></tr>";
    html+= "</table><br><br><button onclick=\"saveInfo()\">Save</button>";
    
    $("#viewmid").html(html);
    var buttons="<button id=\"backbutton\" onclick=\"infoView()\">Back</button>";
    $("#backbutton").remove();
    $("#modalbox").append(buttons);
    $("#modalbox").removeClass();
    $("#modalbox").addClass("infobox");
}

function saveInfo() {
    $.post("/saveinfo", {classname:currentClass, sid:currentStudent['id'],
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
    var calendarTable = "<table><tr><th>Absences: " +
	currentStudent["absent"].length + "</th><th>Latenesses: " +
	currentStudent["late"].length + "</th><th>Excused: " +
	currentStudent["excused"].length + "</th></tr>";
    calendarTable += "<tr><td><div id=\"abscal\"></div></td>"
    calendarTable += "<td><div id=\"latcal\"></div></td>"
    calendarTable += "<td><div id=\"exccal\"></div></td>"
    calendarTable += "</tr></table>"
    
    var html= calendarTable;
    html+= "<button type=\"button\" onclick=\"changeAttendance(" +
	currentStudent["id"] +
	")\">Change Attendance</button>";
    $("#viewmid").html(html);
    var buttons = "<button id=\"backbutton\" onclick=\"studentInfo(" + currentStudent['id'] + ")\">Back</button>";
    $("#modalbox").append(buttons);
    
    $("#abscal").datepick({"dateFormat":"m-d-yyyy",
                          "multiSelect":20});
    $("#latcal").datepick({"dateFormat":"m-d-yyyy",
                          "multiSelect":20});
    $("#exccal").datepick({"dateFormat":"m-d-yyyy",
                          "multiSelect":20});
    $("#abscal").datepick("setDate", currentStudent["absent"]);
    $("#latcal").datepick("setDate", currentStudent["late"]);
    $("#exccal").datepick("setDate", currentStudent["excused"]);
    
    $("#modalbox").removeClass();
    $("#modalbox").addClass("attendancebox");
}

function changeAttendance( id ) {
    
    abs = formatDateArray( $("#abscal").datepick("getDate") );
    lat = formatDateArray( $("#latcal").datepick("getDate") );
    exc = formatDateArray( $("#exccal").datepick("getDate") );
    
    $.post("/changeattendance", {classname:currentClass, sid:id,
           absent:abs.join("_"),
           late:lat.join("_"),
           excused:exc.join("_")});
}
//END ATTENDANCE VIEW FUNCTONS


//WORK VIEW FUNCTIONS
function workView() {
    var gradeInfo = "<table border=\"0\">";
    var totalPoints = [0,0,0];
    var maxPoints = [0,0,0];
    gradeInfo+= getWorkRow('work');
    gradeInfo+= getWorkRow('tests');
    gradeInfo+= getWorkRow('projects');
    gradeInfo += "</table>";
    
    $("#workview").remove();
    $("#modalbox").removeClass();
    $("#modalbox").addClass("workbox");
    $("#viewmid").html( gradeInfo )
    var buttons = "<button id=\"backbutton\" onclick=\"studentInfo(" + currentStudent['id'] + ")\">Back</button>";
    $("#backbutton").remove();
    $("#modalbox").append(buttons);
}

function getWorkRow( type ) {
    var word = type[0].toUpperCase() + type.slice(1);
    var gradeInfo = "<tr><td>" + word + "</td>";
    var totalPoints = 0;
    var maxPoints = 0;
    
    for (var i=0; i<currentStudent[type].length; i++) {
	p = parseFloat(currentStudent[type][i]['points']);
	if ( p != -1 ) {
            totalPoints+= p;
            maxPoints+= parseFloat(currentStudent[type][i]['max']);
	}
    }
    gradeInfo += "<td>" + totalPoints + "/" + maxPoints + "</td><td>";
    if ( maxPoints == 0 )
        gradeInfo+= "-</td></tr>";
    else
        gradeInfo+= (totalPoints/maxPoints * 100).toFixed(2) + "%</td><td><button onclick=\"fullWorkReport('" + type + "', " + totalPoints + ", " + maxPoints + ")\">Full View</button></td></tr>";
    
    return gradeInfo;
}

function fullWorkReport( type, total, max ) {
    var word = type[0].toUpperCase() + type.slice(1);
    var html= "<div id=\"workview\"><center><h3>" + word + " summary: " + total + "/" + max + " ";
    if ( max == 0 )
        html+= "-</h3></center>";
    else
        html+= (total/max * 100).toFixed(2) + "%</h3></center>";
    
    var missing = new Array();
    var excused = new Array();
    var workTable = "<br>All Assignments<br><table border=\"0\">"
    var ca = 0;
    var numAssignments = currentStudent[type].length;
    var wrows = Math.ceil( Math.sqrt( numAssignments ));
    var wcols = wrows;
    if ( numAssignments < wcols * wcols  &&
        wcols * ( wrows - 1) >= numAssignments ) {
        wrows = wrows - 1;
    }
    
    for (var r=0; r < wrows; r++) {
        workTable+= "<tr>";
        
        for (var c=0; c < wcols; c++) {
            if ( ca < numAssignments ) {
                var name = currentStudent[type][ca]['name'];
                var points = currentStudent[type][ca]['points'];
                var maxPoints = parseFloat(currentStudent[type][ca]['max']);
                workTable+= "<td><a onclick=\"gradeChangeView('" + ca + "', '" + type + "', '" + currentStudent['id'] + "')\"><u>"+  name +" ";
                if ( points == 0 )
                    missing.push( name );
		if ( points == -1 ) {
		    excused.push( name );
		    workTable+= "E</u></a></td>";
		}
		else
		    workTable+= points + "/" + maxPoints + "</u></a></td>";
                ca++;
            } //end if assignment exists
            else
                workTable+= "<td> </td>";
        } //end col
        workTable+= "</tr>"
    } //end work table
    workTable+= "</table>"
    
    if ( missing.length == 0 )
        html+= "Missing: -"
    else
        html+= "Missing: " + missing;
    if ( excused.length == 0 )
        html+= "<br>Excused: -"
    else
        html+= "<br>Excused: " + excused;

    html+= "<br>" + workTable + "</div>";
    
    $("#backbutton").remove();
    $("#viewmid").html( html );
    var buttons = "<button id=\"backbutton\" onclick=\"workView()\">Back</button>"
    $("#modalbox").append(buttons);
}

function gradeChangeView(ca, type, id) {
    var name = currentStudent[type][ca]['name'];
    var points = currentStudent[type][ca]['points'];
    var maxPoints = parseFloat(currentStudent[type][ca]['max']);
    
    var html = "<center>Change Grade</center>"
    html+= "Assignment: <b>" + name + "</b> Max Points: <b>" + maxPoints + "</b><br>";
    html+= "Current Grade: <b>";
    if  ( points != -1 )
	html+= points;
    else 
	html+= "E";
    html+= "</b> Change to: <input type=\"text\" size=\"3\" id=\"newgrade\"><br>"
    html+= "<button onclick=\"changeGrade('" + ca + "', '" + type + "', '" + id + "')\">Change Grade</button>";
    
    $("#viewmid").html( html );
}

function changeGrade(ca, type, id) {
    var ng = $("#newgrade").val();
    var newGrade = parseFloat(ng);
    if ( ng == 'e' || ng == 'E' )
	newGrade = -1;
    else if ( isNaN( newGrade ) )
        newGrade = 0;
    currentStudent[type][ca]['points'] = newGrade;
    $.post("/changegrade",{classname:currentClass, atype: type,
           grades:JSON.stringify(currentStudent[type]), sid:id},
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
    $(".student").each(
        function() {
	    if ( parseInt(this.id) >= 1000 ) {
                var g = $(this).find("input").val();
		if ( g == 'e' || g == 'E' )
		    g = -1
                else if ( isNaN(parseFloat(g)) )
                    g = 0;
                else
                    g = parseFloat(g);
                grades[this.id] = g;
            }
        });
    $.post("/savegrades", { classname:currentClass,
			    grades:JSON.stringify(grades),
			    aname:$("#aname").val(),
			    atype:$("[type=radio]:checked").val(), 
			    points:parseFloat($("#amax").val())},
           function(data, status) {
               loadclass( currentClass, M_GRADES);
           });
}
//====== END ASSIGNMENT MODE FUNCTIONS ========


//GRADE MODE FUNCTIONS
function showGrades() {
    
    $.post("/loadclass", { classname : currentClass },
           function( data, status ) {
	       var c = eval("(" + data + ")" );
	       students = c['students'];
           
	       $(".grade").remove();
           
	       for (var i=0; i < students.length; i++) {
		   var grade = computeGrade( students[i], c['weights'] );
		   $("#" + students[i]['id']).append("<div class=\"grade\"><br>"
                                             + grade.toFixed(2) +
                                             "</div>");	       
	       }
           });
}

function computeGrade( student, weights ) {

    var grade = 0;
    var workPart = 0;
    var testPart = 0;
    var projectPart = 0;
    
    workPart = computeGradePart(student['work'], weights['work']); 
    testPart = computeGradePart(student['tests'], weights['tests']);
    projectPart = computeGradePart(student['projects'], weights['projects']);
    
    grade = (workPart + testPart + projectPart) * 100;
    return grade;
}

function computeGradePart(grades, weight){
    var points = 0;
    var max = 0;

    for (var i=0; i < grades.length; i++) {
	if ( grades[i]['points'] != -1 ) {
	    points+= grades[i]['points'];
	    max+= grades[i]['max'];
	}
    }
    var grade = points / max;
    if ( isNaN(grade) )
	grade = 0;
    return grade * weight;
}

function changeWeights() {
    var types = ['work', 'tests', 'projects'];
    var weights = [];
    weights[0] = parseFloat($("#workweight").val());
    weights[1] = parseFloat($("#testweight").val());
    weights[2] = parseFloat($("#projectweight").val());
    
    for (var i=0; i < weights.length; i++)
        if ( isNaN( weights[i] ) )
            weights[i] = 0;
    
    $.post("/changeweights", {classname:currentClass,
			      types: JSON.stringify(types),
			      weights: JSON.stringify(weights)},
           function(data, status) {
               showGrades();
           });
}
//====== END GRADE MODE FUNCTIONS ============
