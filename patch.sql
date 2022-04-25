-- DROP INDEX parcel_unique_where_not_null;
BEGIN;
CREATE UNIQUE INDEX parcel_unique_where_not_null ON parcel (parcelidcnty, deactivatedts)
	WHERE (deactivatedts is null);
ROLLBACK;