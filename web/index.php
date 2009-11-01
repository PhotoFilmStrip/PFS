<?php
$hostname = "localhost";
$database = "webserver";
$username = "webserver";
$password = "JxFz2YjzTfZwC8Zh";

$DB = mysql_connect($hostname, $username, $password) or trigger_error(mysql_error(),E_USER_ERROR); 

mysql_select_db($database, $DB);
mysql_query("update hitcount set counter=counter+1 where id=2");

$lang = $_SERVER['HTTP_ACCEPT_LANGUAGE'];

if (strpos($lang, "de") == 0) {
  header("Location: de/home.html");
} else {
  header("Location: home.html");
}
?>
