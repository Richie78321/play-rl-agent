FROM logstash:8.6.2

WORKDIR /usr/share/logstash

# Download the jbdc output plugin for use with Postgres.
RUN bin/logstash-plugin install logstash-output-jdbc && \
    # Need to download Postgres JDBC manually. See:
    # https://github.com/theangryangel/logstash-output-jdbc/blob/master/README.md#installation
    mkdir -p vendor/jar/jdbc/ && \
    curl -o vendor/jar/jdbc/postgresql-42.6.0.jar https://jdbc.postgresql.org/download/postgresql-42.6.0.jar
