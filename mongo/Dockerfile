FROM mongo:latest

ENV MONGO_INITDB_ROOT_USERNAME test
ENV MONGO_INITDB_ROOT_PASSWORD test
ENV MONGO_INITDB_DATABASE testDB

ADD mongo-init.js /docker-entrypoint-initdb.d/
