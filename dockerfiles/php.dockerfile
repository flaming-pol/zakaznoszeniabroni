FROM php:8.2-apache


# instaluje memcached z PECL
# instaluje mysqli oraz pdo z repo dockera
RUN apt-get update && apt-get install -y libmemcached-dev libssl-dev zlib1g-dev \
	&& pecl install memcached-3.2.0 \
	&& docker-php-ext-enable memcached \
  && docker-php-ext-install mysqli pdo_mysql
