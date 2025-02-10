<?php
require_once 'tools_db.php';
$db = new dbMainCRUD();

$act_id = filter_input(INPUT_GET, 'rozporzadzenie', FILTER_VALIDATE_INT);
if (!$act_id)
  $legal_acts_rows = [];
else
  $legal_acts_rows = $db->get_legal_act_detail($act_id);
$db = null;
?>

<!DOCTYPE html>
<html lang="pl">

<head>
  <meta charset="utf-8">
  <title>ZakazNoszeniaBroni.pl</title>
  <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
  <link rel="icon" href="/favicon.ico" type="image/x-icon">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/js/bootstrap.min.js"></script>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/css/bootstrap.min.css">

  <link rel="stylesheet" href="style.css?v=3">
</head>

<body>
	<div id="main">
    <h1>zakaznoszeniabroni.pl</h1>
    <div id="detale">
<?
if (count($legal_acts_rows) < 1) {
  echo '<div id="msg_container"><div class="msg_fail">';
  echo '<p>oh, nie znaleziono rozporzadzenia o takim identyfikatorze,<br>lub rozporządzenie nie ma wyekstrahowanych szczegółów!</p>';
  echo '</div></div>';
} else {
  echo 'Rozporządzenie <b>' . $legal_acts_rows[0]["number"] . '/' . $legal_acts_rows[0]["year"] . '</b><br>';
  echo 'Data publikacji: ' . $legal_acts_rows[0]["published_date"] . '<br>';
  echo '<a href="' . $legal_acts_rows[0]["pdf_url"] . ' " target="_blank">Link do PDF</a><br>';
  echo 'Obowiązuje na obszarze: <br>';
  $is_active = false;
  $last_area = "";
  $i = 0;
  $array_len = count($legal_acts_rows);
  foreach ($legal_acts_rows as $row) {
    $i++;
    $area = $row["area"];
    if ($last_area != $area) {
      if ($last_area != "") echo '<br>';
      echo ' -- <b>' . $area . '</b> w dniach:';
      $last_area = $area;
    }
    $t_begin = new DateTime($row["begin"]);
    $t_end = new DateTime($row["end"]);
    $t_today = new DateTime();
    if ($t_begin && $t_end) {
      $time_diff = $t_end->getTimestamp() - $t_begin->getTimestamp();
      if ($t_begin->getTimestamp() < $t_today->getTimestamp() &&
          $t_end->getTimestamp() > $t_today->getTimestamp()){
            $active_wrapper = true;
            $is_active = true;
      } else
        $active_wrapper = false;

      if ($active_wrapper) echo '<font color="red">';
      if ($time_diff < 86400)
        echo ' <b>' . $t_begin->format("d-m-Y") . '</b>';
      else
        echo ' od <b>' . $t_begin->format("d-m-Y") . '</b> do <b> ' . $t_end->format("d-m-Y") . '</b>';
      if ($i != $array_len) echo ",";
      if ($active_wrapper) echo '</font>';
    }
  }
  if ($is_active) echo '<br><br><b><font color="red">UWAGA! Zakaz obowiązuje!</font></b><br>';
}

?>
    </div>
  </div>
</body>
</html>
