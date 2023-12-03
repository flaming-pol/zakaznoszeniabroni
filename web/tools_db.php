<?php
class dbBase {
  protected $sql_conn = NULL;
  protected $memcached_conn = NULL;
  protected $config = NULL;

  public function __construct() {
    require_once 'config.php';
    $this->config = $config;
    //$this->memcached_open();
  }

  function __destruct() {
    $this->sql_conn = NULL;
    if ($this->memcached_conn) $this->memcached_conn->quit();
  }

  protected function sql_open() {
    if (!$this->sql_conn){
      $dsn = 'mysql:dbname='. $this->config->dbName .';host='. $this->config->dbHost . ';charset=utf8mb4';
      $options = [
        PDO::ATTR_EMULATE_PREPARES   => false,
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
      ];
      try {
        $this->sql_conn = new PDO($dsn, $this->config->dbUser, $this->config->dbPass, $options);
      } catch (PDOException $e) {
        die("PDO error: " . $e->getMessage());
      }
    }
  }

  protected function memcached_open() {
    if (!$this->memcached_conn) {
      $this->memcached_conn = new Memcached('mc');
      $this->memcached_conn->addServer($this->config->memcachedHost, $this->config->memcachedPort);
    }
  }

  public function cache_lookup($sql) {
    $this->memcached_open();
    $key = 'KEY' . md5($sql);
    $c_result = $this->memcached_conn->get($key);
    if ($c_result) return $c_result;
    $rows = $this->fetch($sql);
    $this->memcached_conn->set($key, $rows, time() + $this->config->memcachedExpire);
    return $rows;
  }

  protected function fetch($sql, $params=null) {
    $this->sql_open();
    $stmt = $this->sql_conn->prepare($sql);
    $stmt->execute($params);
    $data = $stmt->fetchAll();
    $stmt = NULL;
    return $data;
  }

  protected function execute($sql, $params) {
    $this->sql_open();
    $stmt = $this->sql_conn->prepare($sql);
    $stmt->execute($params);
    $stmt = NULL;
  }
}


class dbMainCRUD extends dbBase {
  public function get_legal_acts() {
    $sql = "SELECT name, number, year, pdf_url, published_date FROM rozporzadzenia ORDER BY year DESC, number DESC LIMIT 500";
    $rows = $this->cache_lookup($sql);
    if (count($rows) == 0) die("brak rekordów w bazie!");
    return $rows;
  }

  public function get_statistics() {
    $sql = "SELECT last_parse_du, last_update_db from statystyki LIMIT 1";
    $rows = $this->cache_lookup($sql);
    if (count($rows) == 0) die("brak rekordów w bazie!");
    return $rows;
  }
}


class dbUserCRUD extends dbBase {
  public function get_user_by_email($email) {
    $sql = "SELECT id from users WHERE email=:email LIMIT 1";
    $rows = $this->fetch($sql, ['email' => $email]);
    return $rows;
  }

  public function get_user_by_key($key) {
    $sql = "SELECT id from users WHERE confirmation=:key LIMIT 1";
    $rows = $this->fetch($sql, ['key' => $key]);
    return $rows;
  }

  public function get_inactive_user_by_key($key) {
    $sql = "SELECT id from users WHERE confirmation=:key AND is_active=0 LIMIT 1";
    $rows = $this->fetch($sql, ['key' => $key]);
    return $rows;
  }

  public function activate_user($key) {
    $sql = "UPDATE users SET is_active=1 WHERE confirmation=:key";
    $this->execute($sql, ['key' => $key]);
  }

  public function delete_user($id) {
    $del_notif = "DELETE from notifications WHERE user_id=:id";
    $this->execute($del_notif, ['id' => $id]);

    $del_user = "DELETE from users WHERE id=:id";
    $this->execute($del_user, ['id' => $id]);
  }

  public function add_user($email) {
    $sql = "INSERT INTO users (email, is_active) VALUES (:email, 0)";
    $this->execute($sql, ['email' => $email]);
  }
}
?>
