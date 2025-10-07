# SQLite Practice

Below, we see our query results from the `university_rankings` database.

We run our SQL queries in a single script denoted by `university.sql`.

We first use the `INSERT INTO` and `VALUES` commands to put the data into the table for Duke Tech. \
![Query1](SQL_SS/Q1.png)

We simply select the count and project that of the institutions in global top 200 in 2013. \
![Query2](SQL_SS/Q2.png)

Use the `UPDATE` and `SET` commands to update the score for Oxford in 2014. \
![Query3](SQL_SS/Q3.png)

Delete the scores from the table using the `DELETE FROM` command.
![Query4](SQL_SS/Q4.png)

We can also run our python script which has all our queries input as well.

```bash
python queries.py
```