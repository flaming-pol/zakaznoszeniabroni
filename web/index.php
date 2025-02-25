<?php
//  ZakazNoszeniaBroni.pl -- frontend.
//  Copyright (C) 2023-2025  mc (kontakt@zakaznoszeniabroni.pl)
//
//  This program is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <https://www.gnu.org/licenses/>.

$time_start = microtime(true);

require_once 'tools_db.php';
$db = new dbMainCRUD();

$legal_acts_rows = $db->get_legal_acts();
$stats_rows = $db->get_statistics();
$stats_row = $stats_rows[0];

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

  <script type="text/javascript">
    function showHideRow(row) {
      $("*[id^="+row+"]").toggle();
    }
  </script>
</head>

<body>
	<div id="main">
    <h1>zakaznoszeniabroni.pl</h1>
    <p>Chcesz otrzymywać powiadomienia e-mail o nowych zakazach? <a href="rejestracja.php"> Zarejestruj się! </a></p>
    <br>
		<table border=1 id="tabelka" align=center cellpadding=10>

          <tr>
            <th width=104px>Data publikacji</th>
            <th width=97px>Numer</th>
            <th>Nazwa</th>
            <th width=51px>PDF</th>
            <th width=99px>Szczegóły</th>
          </tr>

<?php
$year = 0;
$i = 0;
$j = 0;

foreach ($legal_acts_rows as $row) {
  $r_id = $row["id"];
  $r_year = $row["year"];
  $r_number = $row["number"];
  $r_name = $row["name"];
  $r_date = $row["published_date"];
  $r_link = $row["pdf_url"];
  $r_enriched = $row["enriched"];
  if ($r_enriched)
    $detale = sprintf("<a href=\"detale.php?rozporzadzenie=%d\">Szczegóły</a>", $r_id);
  else
    $detale = " ";

  // napis pokaż więcej
  if ($i == 5) {
      echo '
            <tr id="x_rok_link">
              <td colspan=5>
                <a id="x_rok_link" href="javascript:void(0);" onclick="showHideRow(\'x_rok_\');">Pokaż więcej</a>
              </td>
            </tr>
  ';
    }
  // naglowek z rokiem
  if ($i < 5) {
    $table_caption_id = "rok_" . $r_year;
    $table_caption_clsss = "rok_row";

  } else {
    $table_caption_id = "x_rok_" . $r_year;
    $table_caption_clsss = "rok_row_hidden";
  }
  if ($year != $r_year) {
    $year = $r_year;
    $j = 1;
    $i++;

    echo '
          <tr id="' . $table_caption_id . '" class="' . $table_caption_clsss . '">
            <td colspan=5 class="rok_row" onclick="showHideRow(\'r_'. $r_year . '_\');">
              <b>' . $r_year . '</b>
            </td>
          </tr>
';
  }

  // rekord z rozporzadzeniem
  if ($year > 2023)
    $is_active = check_if_active($db, $r_id);
  else
    $is_active = false;
  if ($i == 1 && $is_active)
    $class = "alarm";
  elseif ($i == 1 && !$is_active)
    $class = "";
  elseif ($i != 1 && $is_active)
    $class = "hidden_active_row";
  else
    $class = "hidden_row";
  echo '
          <tr id="r_'. $r_year . '_' . $j . '" class="' . $class . '">
            <td>' . $r_date . '</td>
            <td>' . $r_number . '/' . $r_year . '</td>
            <td>' . $r_name . '</td>
            <td><a href="' . $r_link . '" target="_blank">Link</a></td>
            <td>' . $detale . '</td>
          </tr>
  ';
  $j++;
}

$db = null;
?>
		</table>
	</div>
	<div id="kontakt">
    <b>Uwaga:</b> strona ma charakter hobbystyczny. Autor nie ponosi odpowiedzialności za zgodność publikowanych treści z aktualnie obowiązującym prawem.
    Korzystasz na własną odpowiedzialność. Pamiętaj, że oficjalnym źródłem informacji o obowiązujących ustawach i rozporządzeniach jest <a href="https://dziennikustaw.gov.pl" target="_blank">https://dziennikustaw.gov.pl</a>
    <br><br>
    Projekt <i>zakaznoszeniabroni.pl</i> jest oprogramowaniem open source publikowanym na licencji <a href="https://www.gnu.org/licenses/gpl-3.0.html#license-text" target="_blank">GPLv3</a>.
    Kod źródłowy znajduje się w serwisie GitHub - <a href="https://github.com/flaming-pol/zakaznoszeniabroni" target="_blank">link do repozytorium</a>.
    <br><br>
    Masz uwagi do działania strony? Napisz maila na: <a href="mailto:kontakt@zakaznoszeniabroni.pl" target="_blank">kontakt@zakaznoszeniabroni.pl</a>
	</div>
	<div id="stopka">
    <table border=0 id="tabstopka" cellpadding=2>
      <tr>
        <td>Ostatnie uruchomienie parsera:  </td>
        <td><?php echo $stats_row["last_parse_du"] ?></td>
      </tr>
      <tr>
        <td>Ostatnia aktualizacja bazy danych:  </td>
        <td><?php echo $stats_row["last_update_db"] ?></td>
      </tr>
      <tr>
        <td>Czas wykonania skryptu PHP:  </td>
        <td><?php echo number_format((microtime(true) - $time_start), 4) ?></td>
      </tr>
    </table>
	</div>
</body>

</html>
