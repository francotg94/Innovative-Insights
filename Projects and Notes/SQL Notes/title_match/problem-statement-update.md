The data used for the title match, proof of ownership, and property duplicate logic is currently stored in the title_match_log table. There are a few issues with that table that have been brought up and need to be addressed.

- Table Size: the size of the table in Production is ~2gb+. Older data can/should be partitioned.

- Table name: The name of the table is not representative of its function. The table could be renamed in order to properly convey the purpose of the table. We could also create a new table to store the information we need for each project more efficiently and leave the name of the table as it is so it truly acts as a log.

Table and columns in Question:

`title_match_log`
| project_id    | title_report_jsonb | address | report_matched? | ... |
| :------------ | :----------------- | :------ | :-------------- | :-- |
| `varchar(32)` | `jsonb`            | `text`  | `boolean`       | `...` |


There are other columns in the `title_match_log` table but they are unimportant.

A new table should be created and data from the old table should be migrated to this table.

the new table should look like this.

`title_match_source`
| project_id    | apn      | address | report_matched? |
| :---------    | :------- | :------ | :-------------- |
| `varchar(32)` | `text`   | `text`  | `boolean`       |

The `apn` field is a jsonb field within the `title_report_jsonb` column

create the new table `title_match_source` to store our migration data.

Write a query to extract and migrate all the data necessary from `title_match_log` into `title_match_source`.

example `title_match_log` row


| project_id    | title_report_jsonb | address | report_matched? | ... |
| :------------ | :----------------- | :------ | :-------------- | :-- |
| 1c5921ae74da4303bc1fae74363e034c | "{"apn": "123FD-UBB-ACCD", "name-on-report": "dingle berry"}" | 1234 Dingleberry Lane, Ballstown, Uranus 69420  | true       | `...` |


--Making sure I'm working in the right schema within the postgres database
SET search_path TO "Scratch_Database";

--Creating title_match_log table to simulate the problem statement
CREATE TABLE IF NOT EXISTS title_match_log (
    project_id VARCHAR(32),
    title_report_jsonb jsonb,
    address TEXT,
    report_matched BOOLEAN
);

--Creating title_match_source table with column types specified
CREATE TABLE IF NOT EXISTS title_match_source (
    project_id VARCHAR(32),
    apn TEXT,
    address TEXT,
    report_matched BOOLEAN
);

-- Example inserts for title_match_log to simulate the problem statement
INSERT INTO "Scratch_Database".title_match_log (
    project_id,
    title_report_jsonb,
    address,
    report_matched
)
VALUES (
    '1c5921ae74da4303bc1fae74363e034c',
    '{"apn": "123FD-UBB-ACCD", "name-on-report": "dingle berry"}'::jsonb,
    '1234 Dingleberry Lane, Ballstown, Uranus 69420',
    true
    ),
    (
    '2a3456ae74da4303bc1fae74363e034c',
    '{"apn": "ABC-XYZ-1234", "name-on-report": "Jane Doe"}'::jsonb,
    '456 Imaginary Rd, Fakesville, Mars 88888',
    false
    ),
    (
    '3c9876be65da4303bc1fae74363e999z',
    '{"apn": "987FD-PLL-PQQD", "name-on-report": "John Smith"}'::jsonb,
    '789 Berry Patch Ave, Berrytown, Earth 12345',
    true
    ),
    (
    '4d1234ce74da4303bc1fae74363e123x',
    '{"apn": "ZYX-321-ABCD", "name-on-report": "George Citizen"}'::jsonb,
    '1001 Pine Cone Ln, Pineville, Earth 99999',
    false
    );

--This query will take the data requested from 'title_match_log' and insert it into your new table 'title_match_source'.
--It will find the keyword 'apn' in the json file and will return its values as text
INSERT INTO "Scratch_Database".title_match_source (project_id, apn, address, report_matched)
SELECT
    project_id,
    title_report_jsonb ->> 'apn' AS apn,
    address,
    report_matched
FROM "Scratch_Database".title_match_log;

