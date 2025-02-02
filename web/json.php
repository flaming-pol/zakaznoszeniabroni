<?php
header('Content-Type: application/json; charset=utf-8');

require_once 'tools_db.php';

$db = new dbMainCRUD();

$legal_acts_rows = $db->get_legal_acts();
$stats_rows = $db->get_statistics();
$stats_row = $stats_rows[0];

foreach ($legal_acts_rows as &$row) {
  $row["details"] = array();
  if (!$row["enriched"]) continue;
  $details = $db->get_legal_act_detail($row["id"]);
  $last_area = "";
  $y = null;
  foreach ($details as $detail) {
    if ($last_area != $detail["area"]) {
      if ($y) array_push($row["details"], $y);
      $y = array("area" => $detail["area"], "dates" => []);
      $last_area = $detail["area"];
    }
    $y["dates"][] = array("begin" => $detail["begin"], "end" => $detail["end"]);
  }
  $row["details"][] = $y;
}

$db = null;

$data = [
  'version'         => 2,
  'last_parser_run' => $stats_row["last_parse_du"],
  'last_db_update'  => $stats_row["last_update_db"],
  'count'           => count($legal_acts_rows),
  'data'            => $legal_acts_rows,
];
echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);
?>
