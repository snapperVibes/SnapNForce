
CREATE TEMP VIEW v AS
	SELECT addressid, lastupdatedts FROM mailingaddress ma
		JOIN (
			SELECT street_streetid, bldgno, count(*)
			FROM mailingaddress
			GROUP BY street_streetid, bldgno
			HAVING count(*) > 1
		) as dups
		ON ma.bldgno = dups.bldgno AND ma.street_streetid = dups.street_streetid;
ROLLBACK ;
-- SELECT SUM(dups.count)
-- 	FROM (
--   	SELECT street_streetid, bldgno, count(*)
-- 			FROM mailingaddress
-- 			GROUP BY street_streetid, bldgno
-- 			HAVING count(*) > 1
-- 	) as dups;


