BEGIN;
-- New Linked object role
INSERT INTO linkedobjectrole (lorid, lorschema, title, description, createdts, deactivatedts, notes) VALUES
	(233, 'ParcelMailingaddress', 'owner mailing address', null, now(), null, null), (234, 'ParcelMailingaddress', 'mortgage mailing address', null, now(), null, null);

-- ALTER TABLE public.parcelmailingaddress ADD CONSTRAINT parcelmailingaddress_mailingaddressid_fk
--     FOREIGN KEY (mailingparcel_mailingid) REFERENCES mailingaddress (addressid);
-- ALTER TABLE public.parcelmailingaddress RENAME COLUMN mailingparcel_parcelid  TO parcel_parcelkey;
-- ALTER TABLE public.parcelmailingaddress RENAME COLUMN mailingparcel_mailingid TO mailingaddress_addressid;

ALTER TABLE mailingaddress
	ADD COLUMN attention text,
  ADD COLUMN secondary text;

-- Add citystatezip metadata
ALTER TABLE mailingcitystatezip
	ADD COLUMN createdts TIMESTAMP WITH TIME ZONE,
  ADD COLUMN createdby_userid INTEGER
  	CONSTRAINT mailingcitystatezip_created_by_userid_fk REFERENCES login,
	ADD source_sourceid INTEGER
    CONSTRAINT mailingcitystatezip_sourceid_fk REFERENCES bobsource,
	ADD lastupdatedts TIMESTAMP WITH TIME ZONE,
	ADD lastupdatedby_userid INTEGER
    CONSTRAINT mailingcitystatezip_lastupdatedby_userid_fk REFERENCES login,
	ADD deactivatedts TIMESTAMP WITH TIME ZONE,
	ADD deactivatedby_userid INTEGER
    CONSTRAINT mailingcitystatezip_deactivatedby_userid REFERENCES login;
-- Add default id
CREATE SEQUENCE mailingcitystatezip_id_seq START 300000;
ALTER TABLE mailingcitystatezip ALTER column id SET DEFAULT nextval('public.mailingcitystatezip_id_seq'::regclass);

-- Ease mailing constraints
ALTER TABLE mailingaddress
	ALTER COLUMN bldgno DROP not null;
UPDATE mailingstreet SET pobox=false WHERE pobox IS NULL;
ALTER TABLE mailingstreet
	ALTER COLUMN pobox SET NOT NULL;

-- The human_id_seq is currently set to 100 when a developer loads a fresh copy of the database
--  This causes id collisions when inserting new humans.
--  This hacky solution fixes that.
--  Note: other tables likely share this same problem. We can deal with it when we run into it.
select setval('public.human_humanid_seq'::regclass, max(humanid) + 30000) from human;


-- AT THIS POINT, RUN consolidate.py


UPDATE public.linkedobjectrole SET (lorschema, title, description, deactivatedts, notes) =
  ('MailingaddressHuman', 'Owner mailing address', 'The address listed at the bottom of the county profile page', '2022-02-18 16:45:47.278684-05', NULL) WHERE lorid = 103;
DELETE FROM public.linkedobjectrole WHERE lorid = 233;
DELETE FROM public.linkedobjectrole WHERE lorid = 234;
INSERT INTO public.linkedobjectrole (lorid, lorschema, title, description, createdts, deactivatedts, notes) VALUES

	-- TODO: SHOULD THIS BE MailingAddressHuman?
  (234, 'MailingaddressHuman', 'Tax Bill Mailing Address', 'The address listed under the "Tax Bill Mailing Address"', now(), NULL, NULL),

	-- And this would be the only "ParcelMailingAddress"
	(235, 'ParcelMailingaddress', 'County property address', 'The address listed to the left of the Owner Name on county website', now(), NULL, NULL),

  (236, 'ParcelHuman', 'Tax Bill Mailing Addressee', 'The name listed above the Tax Bill Mailing Address', now(), NULL, NULL),
	(237, 'ParcelHuman', 'Owner Name', 'The name listed as "Owner Name:" in the upper right of the county profile page', now(), NULL, NULL);
COMMIT;
