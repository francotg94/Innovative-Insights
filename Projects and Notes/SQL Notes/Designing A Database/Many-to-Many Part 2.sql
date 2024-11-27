INSERT INTO book VALUES(
  'Learn PostgreSQL Volume 1',
  '123457891',
  100,
  2.99,
  'Manage database part one',
  'Codecademy'
);

INSERT INTO book VALUES(
  'Learn PostgreSQL Volume 2',
  '987654321',
  200,
  3.99,
  'Manage database part two',
  'Codecademy'
);

SELECT *
FROM book;

INSERT INTO author VALUES (
  'James Key',
  'Guru in database management with PostgreSQL',
  'jkey@db.com'
);

INSERT INTO author VALUES (
  'Clara Index',
  'Guru in database management with PostgreSQL',
  'cindex@db.com'
);

SELECT *
FROM author;

INSERT INTO books_authors VALUES (
  '123457890',
  'jkey@db.com'
);

UPDATE books_authors
    SET book_isbn = '123457891'
WHERE book_isbn = '123457890';

INSERT INTO books_authors VALUES (
  '123457890',
  'cindex@db.com'
);

INSERT INTO books_authors VALUES (
  '987654321',
  'cindex@db.com'
);

SELECT book.title AS book_title, author.name AS author_name, book.description AS book_description
FROM book, author, books_authors
WHERE book.isbn = books_authors.book_isbn
AND author.email = books_authors.author_email;

SELECT author.name AS author_name, author.email AS author_email, book.title AS book_title
FROM book
JOIN books_authors
ON book.isbn = books_authors.book_isbn
JOIN author
ON books_authors.author_email = author.email;