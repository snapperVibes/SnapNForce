-- Several tables contain multiple values that tuples that refer to the same real-world data.
--  This file contains statements to make the issues easily viewable.
--  Running `consolidate.py` fixes these issues.

--
-- MAIN TABLES

-- VIEW DUPLICATE MAILINGADDRESSES
SELECT array_agg(addressid) addressids, bldgno, street_streetid, attention, secondary
	FROM mailingaddress
	GROUP BY bldgno, street_streetid, attention, secondary, deactivatedts
	HAVING count(*) > 1 AND deactivatedts IS null;

-- VIEW DUPLICATE PARCELS
SELECT array_agg(parcelkey), parcelidcnty
	FROM parcel
	GROUP BY parcelidcnty, deactivatedts
	HAVING count(*) > 1 AND deactivatedts IS null;

--
-- LINKING TABLES

-- VIEW DUPLICATE PARCELMAILINGADDRESSES
WITH dups AS (
	SELECT array_agg(linkid) linkids, parcel_parcelkey, mailingaddress_addressid, linkedobjectrole_lorid FROM parcelmailingaddress pma
		GROUP BY parcel_parcelkey, mailingaddress_addressid, linkedobjectrole_lorid, pma.deactivatedts
		HAVING count(*) > 1 AND pma.deactivatedts IS null
) SELECT dups.linkids, dups.parcel_parcelkey, dups.mailingaddress_addressid, dups.linkedobjectrole_lorid, ma.bldgno, ma.street_streetid, ma.attention, ma.secondary, p.parcelidcnty  FROM dups
		JOIN parcel p on dups.parcel_parcelkey=p.parcelkey
		JOIN mailingaddress ma on dups.mailingaddress_addressid=ma.addressid;

-- VIEW DUPLICATE HUMANPARCELS
SELECT  array_agg(linkid) linkids, human_humanid, parcel_parcelkey
	FROM humanparcel
	GROUP BY  human_humanid, parcel_parcelkey, source_sourceid, linkedobjectrole_lorid,deactivatedts
	HAVING count(*) > 1 AND deactivatedts IS null;

-- VIEW DUPLICATE PARCELUNITS
SELECT array_agg(unitid) unitids, unitnumber, parcel_parcelkey
	FROM parcelunit
	GROUP BY unitnumber, parcel_parcelkey, deactivatedts
	HAVING count(*) > 1 AND deactivatedts IS null;
