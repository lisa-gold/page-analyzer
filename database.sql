CREATE TABLE urls (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) UNIQUE,
    created_at timestamp);
    