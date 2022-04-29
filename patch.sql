


BEGIN ;
-- DROP INDEX parcel_unique_where_not_null;
CREATE UNIQUE INDEX parcel_unique_where_not_null ON parcel (parcelidcnty)
	WHERE (deactivatedts is null);
COMMIT;
ROLLBACK;


ALTER TABLE mailingaddress
	ALTER COLUMN bldgno DROP not null;

-- 	ALTER TABLE mailingaddress
-- 		ADD CONSTRAINT at_least_one_of_bldgno_or_attention_not_null
-- 		CHECK ((bldgno IS NOT NULL) or (attention IS NOT NULL));
UPDATE mailingstreet SET pobox=false WHERE pobox IS NULL;

CREATE SEQUENCE mailingcitystatezip_id_seq START 300000;
ALTER TABLE mailingcitystatezip ALTER column id SET DEFAULT nextval('public.mailingcitystatezip_id_seq'::regclass);

BEGIN;
ALTER TABLE mailingaddress ADD COLUMN secondary text;
COMMIT;

