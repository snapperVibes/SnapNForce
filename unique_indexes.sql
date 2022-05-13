CREATE UNIQUE INDEX IF NOT EXISTS mailingaddress_unique_where_not_null
	ON mailingaddress (bldgno, attention, secondary)
	WHERE (deactivatedts is null);

CREATE UNIQUE INDEX IF NOT EXISTS parcel_unique_where_not_null
	ON parcel (parcelidcnty)
	WHERE (deactivatedts is null);

CREATE UNIQUE INDEX IF NOT EXISTS parcelmailingaddress_unique_where_not_null
	ON parcelmailingaddress (parcel_parcelkey, mailingaddress_addressid, linkedobjectrole_lorid)
	WHERE (deactivatedts is null);
