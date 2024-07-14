--This sequence of SQL queries will create the following tables if they don't already exist
--The goal below is to create a schema in PostgreSQL that connects these tables

create table if not exists profile (
name varchar(20),
age integer,
home_address varchar(100),
phone char(10),
home_email varchar(50),
work_address varchar(100),
work_position varchar(20),
work_phone char(10),
work_id varchar(10),
school_id varchar(10),
school_email varchar(50),
school_address varchar(100)
);

create table if not exists book (
title varchar(100),              --Title of book
isbn varchar(50),                --ISBN Number of book
pages integer,                   --Number of pages in the book
price money,                     --Cost of the book
description varchar(256),        --Description of the book
publisher varchar(100)           --Publisher of the book
);

create table if not exists chapter (
book_isbn varchar(50),           -- ISBN of the book to link the chapter
number integer,                  -- Number of the chapter
title varchar(50),               -- Title of Chapter
content varchar(1024)            -- Content within the chapter
);

create table if not exists author (
name varchar(50),
bio varchar(100),
email varchar(100)
);