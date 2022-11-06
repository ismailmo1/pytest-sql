FROM postgres:10-alpine
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
EXPOSE 5432
# seed database with food reference data
COPY ./seed_scripts/food_ref.sql /docker-entrypoint-initdb.d/