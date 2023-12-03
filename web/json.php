<?php
header('Content-Type: application/json; charset=utf-8');

require_once 'tools_db.php';

$db = new dbMainCRUD();

$legal_acts_rows = $db->get_legal_acts();
$stats_rows = $db->get_statistics();
$stats_row = $stats_rows[0];

$db = null;

$data = [
  'version'         => 1,
  'last_parser_run' => $stats_row["last_parse_du"],
  'last_db_update'  => $stats_row["last_update_db"],
  'count'           => count($legal_acts_rows),
  'data'            => $legal_acts_rows,
];
echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);
?>
