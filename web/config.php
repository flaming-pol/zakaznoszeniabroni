<?php
date_default_timezone_set('Europe/Warsaw');
class Config {
  public string $dbHost;
  public string $dbName;
  public string $dbUser;
  public string $dbPass;
  public int $dbPort;
  public string $memcachedHost;
  public int $memcachedPort;
  public int $memcachedExpire;
}
$config = new Config();

// default
$config->dbHost = 'localhost';
$config->dbName = 'mydb';
$config->dbUser = 'myuser';
$config->dbPass = 'mypass';
$config->dbPort = 3306;
$config->memcachedHost = 'localhost';
$config->memcachedPort = 11211;
$config->memcachedExpire = 5;


// zaczytanie zmiennych z enva
if (getenv('DB_SERVER')) $config->dbHost = getenv('DB_SERVER');
if (getenv('DB_NAME')) $config->dbName = getenv('DB_NAME');
if (getenv('DB_USER')) $config->dbUser = getenv('DB_USER');
if (getenv('DB_PASS')) $config->dbPass = getenv('DB_PASS');
if (getenv('DB_PORT')) $config->dbPort = intval(getenv('DB_PORT'));
if (getenv('MEMCACHED_SERVER')) $config->memcachedHost = getenv('MEMCACHED_SERVER');
if (getenv('MEMCACHED_PORT')) $config->memcachedPort = intval(getenv('MEMCACHED_PORT'));
if (getenv('MEMCACHED_EXPIRE')) $config->memcachedExpire = intval(getenv('MEMCACHED_EXPIRE'));

// nadpisanie przy pomocy konfigu lokalnego
if (file_exists(__DIR__ . '/config.local.php')) {
	require_once(__DIR__ . '/config.local.php');
}

?>
