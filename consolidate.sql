WITH duplicate_addresses AS (
	SELECT street_streetid, bldgno, count(*)
		FROM mailingaddress
		WHERE deactivatedts is NULL
		GROUP BY street_streetid, bldgno
		HAVING count(*) > 1
  )