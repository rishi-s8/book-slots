<?php
function build_calendar($month, $year){

  //Creating an array containing names of all days and weeks.
  $daysOfWeek = array('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday');
  
  //Here, we'll get the first day of the month that is in the argument of this function
  $firstDayOfMonth = mktime(0,0,0,$month,1,$year);
  
  //Now getting the number of days this month contains
  $numberDays = date('t', $firstDayOfMonth);
  
  //Getting some information about the first day of this month
  $dateComponents = getdate($firstDayOfMonth);
  
  //Getting the name of this month
  $monthName = $dateComponents['month'];
  
  //Getting the index value 0-6 of the first day of this month
  $dayOfWeek = $dateComponents['wday'];
  
  //Getting the current date
  $datetoday = date('Y-m-d');
  
  //Now creating the HTML table
  $calendar = "<table class='table table-bordered'>";
  $calendar.="<center><h2>$monthName $year</h2></center>";
  
  $calendar.= "<tr>";
  
  //Creating the calendar headers
  foreach($daysOfWeek as $day){
    $calendar.= "<th class='header'>$day</th>";
  }
  
  $calendar.= "</tr><tr>";
  
  //The variable $dayOfWeek will make sure that there must be only 7 columns on our table
  if($dayOfWeek > 0){
    for($k=0;$k<dayOfWeek;$k++){
      $calendar.= "<td></td>";
    }
  }
  
  //Initiating the day counter
  $currentDay = 1;
  
  //Getting the month number
  
  $month = str_pad($month,2,"0",STR_PAD_LEFT);
  
  while($currentDay <= $numberDays){
  
    //if seventh column (saturday) reached, start a new row
    if($dayOfWeek == 7){
      $dayOfWeek = 0;
      $calendar.= "</tr><tr>;
  
    $currentDayRel = str_pad($currentDay,2,"0",STR_PAD_LEFT);
    $date = "$year-$month-$currentDayRel";
    
    $calendar.= "<td><h4>$currentDay</h4>";
    
    $calendar.="</td>";
    
    //Incrementing the counters
    $currentDay++;
    $dayOfWeek++;
    
  }
  
  //completing the row of the last week in month, if necessary
  if($dayOfWeek != 7){
    $remainingDays = 7-$dayOfWeek;
    for($i=0;$i<remainingDays;$i++){
      $calendar.="<td></td>";
    }
  }
  
  $calendar.= "</tr>";
  $calendar.= "</table>";
  
  echo $calendar;
    
}

?>
  
