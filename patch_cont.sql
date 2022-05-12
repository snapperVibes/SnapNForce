BEGIN;
-- DELETE FROM linkedobjectrole WHERE true;
UPDATE public.linkedobjectrole SET (lorschema, title, description, deactivatedts, notes) =
  ('MailingaddressHuman', 'Owner mailing address', 'The address listed at the bottom of the county profile page', '2022-02-18 16:45:47.278684-05', NULL, NULL) WHERE lorid = 103;
INSERT INTO public.linkedobjectrole (lorid, lorschema, title, description, createdts, deactivatedts, notes) VALUES

	-- TODO: SHOULD THIS BE MailingAddressHuman?
  (234, 'ParcelMailingaddress', 'Tax Bill Mailing Address', 'The address listed under the "Tax Bill Mailing Address"', now(), NULL, NULL),

	-- And this would be the only "ParcelMailingAddress"
	(235, 'ParcelMailingaddress', 'County property address', 'The address listed to the left of the Owner Name on county website', now(), NULL, NULL),

                                                                                                                   (236, 'ParcelHuman', 'Tax Bill Mailing Addressee', 'The name listed above the Tax Bill Mailing Address', now(), NULL, NULL),
	(237, 'ParcelHuman', 'Owner Name', 'The name listed as "Owner Name:" in the upper right of the county profile page', now(), NULL, NULL);
ROLLBACK;