ALTER TYPE linkedobjectroleschema ADD VALUE 'GeneralMailingAddress';
ALTER TYPE linkedobjectroleschema ADD VALUE 'MortgageMailingAddress';
BEGIN;
ALTER TABLE public.parcelmailingaddress ADD CONSTRAINT parcelmailingaddress_mailingaddressid_fk
    FOREIGN KEY (mailingparcel_mailingid) REFERENCES mailingaddress (addressid);

ALTER TABLE public.parcelmailingaddress RENAME COLUMN mailingparcel_parcelid TO parcel_parcelkey;
ALTER TABLE public.parcelmailingaddress RENAME COLUMN mailingparcel_mailingid TO mailingaddress_addressid;
ALTER TABLE mailingcitystatezip
ADD source_sourceid INTEGER
    CONSTRAINT mailingcitystatezip_sourceid_fk REFERENCES bobsource,
ADD lastupdatedts        TIMESTAMP WITH TIME ZONE,
ADD lastupdatedby_userid INTEGER
    CONSTRAINT mailingcitystatezip_lastupdatedby_userid_fk REFERENCES login,
ADD deactivatedts        TIMESTAMP WITH TIME ZONE,
ADD deactivatedby_userid INTEGER
    CONSTRAINT mailingcitystatezip_deactivatedby_userid REFERENCES login;
INSERT INTO linkedobjectrole (lorid, lorschema_schemaid, title, description, createdts, deactivatedts, notes) VALUES
	(233, 'GeneralMailingAddress', 'general mailing address', null, now(), null, null), (234, 'MortgageMailingAddress', 'mortgage mailing address', null, now(), null, null);

ALTER TABLE mailingaddress
	ADD COLUMN attention text;

ALTER TABLE mailingcitystatezip
	ADD COLUMN createdts TIMESTAMP WITH TIME ZONE;
ALTER TABLE mailingcitystatezip
	ADD COLUMN createdby_userid INTEGER
    CONSTRAINT mailingcitystatezip_createdby_userid_fk REFERENCES login;


-- BEGIN;
-- INSERT INTO mailingstreet (streetid, name, namevariantsarr, citystatezip_cszipid, notes, pobox, createdts, createdby_userid, lastupdatedts, lastupdatedby_userid, deactivatedts, deactivatedby_userid) VALUES
-- 	(-1, 'PO BOX', null, )