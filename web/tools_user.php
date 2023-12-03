<?php
// Funkcje pomocniczne do obsługi użytkowników.

function redir($msg_ok = null, $msg_fail = null) {
  if (!is_null($msg_ok)) $_SESSION["messages_ok"] = $msg_ok;
  if (!is_null($msg_fail)) $_SESSION["messages_fail"] = $msg_fail;
  header('Location: ' . $_SERVER["PHP_SELF"], true, 303);
  exit;
}

function check_key($key) {
  $regex = '/^[a-zA-Z0-9]+$/';
  if (strlen($key) != 256) return false;
  if (!preg_match($regex, $key)) return false;
  return true;
}

function fetch_from_session(&$msg_ok, &$msg_fail) {
  if (isset($_SESSION["messages_ok"])) {
    $msg_ok = $_SESSION["messages_ok"];
    unset($_SESSION["messages_ok"]);
  }
  if (isset($_SESSION["messages_fail"])) {
    $msg_fail = $_SESSION["messages_fail"];
    unset($_SESSION["messages_fail"]);
  }
}
?>
