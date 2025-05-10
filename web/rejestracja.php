<?php
require_once 'tools_db.php';
require_once 'tools_user.php';
$db = new dbUserCRUD();
$msg_ok = [];
$msg_fail = [];

session_start();

$request_method = strtoupper($_SERVER["REQUEST_METHOD"]);

// Dodawanie nowego użytkownika
if ($request_method === "POST") {
  $email = $_POST["email"];

  if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $msg_fail[] = "Podano błędny adres e-mail!";
    redir($msg_ok, $msg_fail);
  }
  if (!isset($_POST["zgoda_na_wysylke"]) or !isset($_POST["zgoda_na_polityke"])) {
    $msg_fail[] = "Aby zapisać swój adres w bazie musisz wyrazić zgodę na otrzymywanie";
    $msg_fail[] = "wiadomości e-mail oraz zaakceptować politykę prywatności.";
    redir($msg_ok, $msg_fail);
  }

  $users = $db->get_user_by_email($email);
  if (count($users) > 0) {
    $msg_fail[] = "Taki adres e-mail jest już w bazie danych.";
    redir($msg_ok, $msg_fail);
  }
  $db->add_user($email);
  $msg_ok[] = "Dodano użytkownika <b>$email</b> do bazy!";
  $msg_ok[] = "Twoje konto wymaga aktywacji. Link aktywacyjny wysłano e-mailem.";
  $msg_ok[] = 'Jeśli e-mail nie dotarł w ciągu 15 minut proszę o informacje na <a href="mailto:kontakt@zakaznoszeniabroni.pl">kontakt@zakaznoszeniabroni.pl</a>';
  redir($msg_ok, $msg_fail);
}

if ($request_method === "GET") {
  fetch_from_session($msg_ok, $msg_fail);

  // Usuwanie użytkownika
  if (isset($_GET["usun"])) {
    $klucz = $_GET["usun"];

    if (!check_key($klucz)) {
      $msg_fail[] = "Błędny format klucza autoryzacyjnego.";
      redir($msg_ok, $msg_fail);
    }
    $users = $db->get_user_by_key($klucz);
    if (count($users) != 1) {
      $msg_fail[] = "Nie ma takiego użytkownika w bazie.";
      redir($msg_ok, $msg_fail);
    }
    $db->delete_user($users[0]["id"]);
    $msg_ok[] = "Usunięto użytkownika z bazy danych.";
    $msg_ok[] = "Jeśli zmienisz zdanie, pamiętaj, że zawsze możesz zarejestrować się ponownie.";
    redir($msg_ok, $msg_fail);
  }

  // Aktywacja użytkownika
  if (isset($_GET["potwierdz"])) {
    $klucz = $_GET["potwierdz"];

    if (!check_key($klucz)) {
      $msg_fail[] = "Błędny format klucza autoryzacyjnego.";
      redir($msg_ok, $msg_fail);
    }
    $users = $db->get_inactive_user_by_key($klucz);
    if (count($users) != 1) {
      $msg_fail[] = "Nie ma takiego użytkownika w bazie,";
      $msg_fail[] = "lub został już aktywowany.";
      redir($msg_ok, $msg_fail);
    }
    $db->activate_user($klucz);
    $msg_ok[] = "Poprawnie aktywowano konto.";
    $msg_ok[] = "Od teraz będziesz informowany o nowych zakazach noszenia broni!";
    redir($msg_ok, $msg_fail);
  }
}

$db = null;
?>
<!DOCTYPE html>
<html lang="pl">

<head>
  <meta charset="utf-8">
  <title>ZakazNoszeniaBroni.pl - rejestracja</title>
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
    <br>
    <?php
    if (!empty($msg_ok) or !empty($msg_fail)) {
      echo '<div id="msg_container">';
      if (count($msg_ok) > 0) {
        echo '<div class="msg_ok">';
        foreach ($msg_ok as $msg) { echo "<p>$msg</p>"; }
        echo '</div>';
      }
      if (count($msg_fail) > 0) {
        echo '<div class="msg_fail">';
        foreach ($msg_fail as $msg) { echo "<p>$msg</p>"; }
        echo '</div>';
      }
      echo '</div>';
      echo '<br>';
    }
    ?>
    <p>Wpisz w poniższe pole swój adres e-mail aby otrzymywać powiadomienia o nowych <i>zakazach noszenia broni</i>.</p>
    <br>
    <br>
      <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
      	<label>e-mail: <input type="text" size="22px" name="email" autocomplete="off"></label>
      	<br><br>
        <div id="checkboxy_zgody">
          <label><input type="checkbox" name="zgoda_na_wysylke"> Wyrażam zgodę na otrzymywanie wiadomości z serwisu <a href="#">zakaznoszeniabroni.pl</a>, w tym informacji handlowych, za pośrednictwem komunikacji e-mail.</label>
          <br>
          <label><input type="checkbox" name="zgoda_na_polityke"> Zapoznałem się i akceptuję <a href="polityka_prywatnosci.pdf" target="_blank">politykę prywatności</a>.</label>
          <br>
        </div>
      	<input type="submit" name="submit" value="Zarejestruj!"/>
      </form>
  </div>
</body>
</html>
