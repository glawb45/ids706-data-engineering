-- Question 1
INSERT INTO university_rankings (institution, country, world_rank, score, year)
VALUES ('Duke Tech', 'USA', 350, 60.5, 2014);

-- Question 2
SELECT country, COUNT(institution) AS count
FROM university_rankings
WHERE world_rank <= 200 AND 
    year = 2013 AND 
    country = 'Japan';

-- Question 3
UPDATE university_rankings 
SET score = score + 1.2
WHERE institution = 'University of Oxford' AND year = 2014;

-- Question 4
DELETE FROM university_rankings
WHERE year = 2015 AND score < 45;

SELECT *
FROM university_rankings;

SELECT institution, country, score, year
FROM university_rankings
WHERE institution = 'University of Oxford' AND year = 2014;

SELECT institution, country, world_rank, score, year
FROM university_rankings
WHERE institution = 'Duke Tech';