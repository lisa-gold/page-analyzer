DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS url_checks;

CREATE TABLE urls (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) UNIQUE,
    created_at date DEFAULT CURRENT_DATE
    );

CREATE TABLE url_checks (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id integer REFERENCES urls (id),
    status_code integer,
    h1 varchar(255),
    title varchar(255),
    description varchar(500),
    created_at date DEFAULT CURRENT_DATE
);
