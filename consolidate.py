"""
One off script to add a database integrity check to ensure
multiple mailingaddress referring to the same building cannot be active at the same time
"""
import itertools
import logging
import os.path

import structlog
from sqlalchemy import text
from sqlalchemy.engine import Connection
from structlog.stdlib import LoggerFactory

from app.constants import USER_ID
from app.database import get_db_context

logging.basicConfig(
    level=logging.DEBUG,
    filename=os.path.join("log", "consolidate.log")
)

structlog.configure(logger_factory=LoggerFactory())
global_logger = structlog.get_logger()
global_logger.format = "%(message)s"




def consolidate_mailing_addresses(conn: Connection, logger, municode):
    for address_ids, _building_number, _street_id, _attention, _secondary, _parcelkey in select_duplicate_address_ids(conn, municode):
        logger.msg("Consolidating mailing addresses", building_number=_building_number, street_id=_street_id, attention=_attention, secondary=_secondary, address_ids=address_ids, parcelkey=_parcelkey)
        truth = address_ids[0]
        dups = address_ids[1:]
        logger.debug("Choose address_id as a source of truth", truth=truth, dups=address_ids)
        update_functions = [
            update_human_mailing_address, update_parcelmailingaddress_by_address
        ]
        for addressid in dups:
            log = logger.bind(address_id=addressid, truth=truth)
            deactivate_addressid(conn, addressid, log=log)
            for func in update_functions:
                func(conn, old=addressid, new=truth, log=log)



def consolidate_parcels(conn: Connection, logger, municode):
    for parcel_keys, _parcelidcnty in select_duplicate_parcel_keys(conn, municode):
        logger.msg("Consolidating parcels", parcel_id_county=_parcelidcnty)
        truth: int = parcel_keys[0]
        dups: list[int] = parcel_keys[1:]
        logger.debug("Choose parcel as a source of truth", truth=truth, dups=dups)
        update_functions = [
            update_parcelmailingaddress_by_parcel,
            update_human_parcel_by_parcel,
            update_parcel_info,
            update_parcelphotodoc,
            update_parcelunit_by_parcel_key,
        ]
        for parcel_key in dups:
            log = logger.bind(parcel_key=parcel_key, truth=truth, parcel_id_county=_parcelidcnty)
            deactivate_parcel(conn, parcel_key)
            for func in update_functions:
                func(conn, old=parcel_key, new=truth, log=log)


def deactivate_duplicate_parcel_mailing_addresses(conn: Connection, logger, municode):
    for linkids, _parcelkey, _mailingaddress_addressid, _linked_object_role,  _bldgno, _street_id, _attn, _secondary, _parcelid_county in select_duplicate_parcel_mailing_addresses(conn, municode):
        logger.msg("Consolidating parcelmailingaddress", parcelkey=_parcelkey, addressid=_mailingaddress_addressid, linked_object_role=_linked_object_role, bldgno=_bldgno, street=_street_id, attn=_attn, secondary=_secondary, parcelid_county=_parcelid_county)
        truth = linkids[0]
        dups: list[int] = linkids[1:]
        logger.debug("Choose parcelmailingaddress as a source of truth", truth=truth, dups=dups)
        deactivate_funcs = [deactivate_parcelmailingaddress_by_link_id]
        for linkid in dups:
            log = logger.bind(linkid=linkid)
            for func in deactivate_funcs:
                func(conn, old=linkid, log=log)


def deactivate_duplicate_human_parcels(conn: Connection, logger, municode):
    for linkids, _humanid, _parcelkey, in select_duplicate_human_parcels(conn, municode):
        logger.info("Consolidating humanparcels", humanid=_humanid, parcelkey=_parcelkey)
        truth = linkids[0]
        dups = linkids[1:]
        logger.info("Choose humanparcel as source of truth", truth=truth, dups=dups)
        deactivate_funcs = [deactivate_human_parcel_by_linkid]
        for linkid in dups:
            log = logger.bind(linkid=linkid)
            for func in deactivate_funcs:
                func(conn, old=linkid, log=log)


def deactivate_duplicate_parcel_units(conn: Connection, logger, municode):
    for unitids, _unnitnumber, _parcelkey,  in select_duplicate_parcel_units(conn, municode):
        logger.info("Consolidating parcel units", unitnumber=_unnitnumber, parcelkey=_parcelkey)
        truth = unitids[0]
        dups = unitids[1:]
        logger.info("Choose parcelunit as source of truth", truth=truth, dups=dups)
        deactivate_funcs = [deactivate_parcelunit_by_unit_id]
        for unitid in dups:
            log = logger.bind(unitid=unitid)
            for func in deactivate_funcs:
                func(conn, old=unitid, log=log)



# @log_return("Selected duplicate address ids: {}")
def select_duplicate_address_ids(conn: Connection, municode):
    statement = text(
        """
        SELECT array_agg(addressid) addressids, bldgno, street_streetid, attention, secondary, null FROM mailingaddress
            GROUP BY bldgno, street_streetid, attention, secondary, deactivatedts
            HAVING count(*) > 1 AND deactivatedts IS null
        """
    )
    if municode:
        statement = text(
            """
            WITH dups AS
            (
                SELECT array_agg(addressid) addressids, bldgno, street_streetid, attention, secondary FROM mailingaddress
                GROUP BY bldgno, street_streetid, attention, secondary, deactivatedts
                HAVING count(*) > 1 AND deactivatedts IS null
            ),
            x AS
            (
            SELECT dups.addressids, dups.bldgno, dups.street_streetid, dups.attention, dups.secondary, pma.parcel_parcelkey
            FROM dups JOIN parcelmailingaddress pma ON pma.mailingaddress_addressid = ANY(dups.addressids)
            ) SELECT x.addressids, x.bldgno, x.street_streetid, x.attention, x.street_streetid, p.muni_municode
                FROM x JOIN parcel p ON x.parcel_parcelkey=p.parcelkey
                WHERE muni_municode=:municode
            """
        ).params({"municode": municode})
    return conn.execute(statement).all()


def select_duplicate_parcel_keys(conn, municode):
    statement = text(
        """
        SELECT array_agg(parcelkey), parcelidcnty FROM parcel
            GROUP BY parcelidcnty, deactivatedts
            HAVING count(*) > 1 AND deactivatedts IS null
        """
    )
    if municode:
        statement = text(
            """
            SELECT array_agg(parcelkey), parcelidcnty FROM parcel
                JOIN municipality on parcel.muni_municode = municipality.municode
                GROUP BY parcelidcnty, deactivatedts, municode
                HAVING count(*) > 1 AND deactivatedts IS null
                AND municipality.municode=:municode
            """
        ).params({"municode": municode})
    return conn.execute(statement).all()


def select_duplicate_parcel_mailing_addresses(conn, municode):
    statement = text(
            """
            WITH dups AS (
              SELECT array_agg(linkid) linkids, parcel_parcelkey, mailingaddress_addressid, linkedobjectrole_lorid FROM parcelmailingaddress pma
                GROUP BY parcel_parcelkey, mailingaddress_addressid, linkedobjectrole_lorid, pma.deactivatedts
                HAVING count(*) > 1 AND pma.deactivatedts IS null
            ) SELECT dups.linkids, dups.parcel_parcelkey, dups.mailingaddress_addressid, dups.linkedobjectrole_lorid, ma.bldgno, ma.street_streetid, ma.attention, ma.secondary, p.parcelidcnty  FROM dups
                JOIN parcel p on dups.parcel_parcelkey=p.parcelkey
                JOIN mailingaddress ma on dups.mailingaddress_addressid=ma.addressid
            """
    )
    if municode:
        statement = text(
            """
            WITH dups AS (
              SELECT array_agg(linkid) linkids, parcel_parcelkey, mailingaddress_addressid, linkedobjectrole_lorid FROM parcelmailingaddress pma
                JOIN parcel p on parcel_parcelkey=p.parcelkey
                GROUP BY parcel_parcelkey, mailingaddress_addressid, linkedobjectrole_lorid, pma.deactivatedts
                HAVING count(*) > 1 AND pma.deactivatedts IS null
            ) SELECT dups.linkids, dups.parcel_parcelkey, dups.mailingaddress_addressid, dups.linkedobjectrole_lorid, ma.bldgno, ma.street_streetid, ma.attention, ma.secondary, p.parcelidcnty  FROM dups
                JOIN parcel p on dups.parcel_parcelkey=p.parcelkey
                JOIN mailingaddress ma on dups.mailingaddress_addressid=ma.addressid
                WHERE p.muni_municode=:municode;
            """
    ).params({"municode": municode})
    return conn.execute(statement).all()


# @log_return("Selected duplicate human parcels: {}")
def select_duplicate_human_parcels(conn, municode):
    statement = text(
        """
            SELECT  array_agg(linkid) linkids, human_humanid, parcel_parcelkey FROM humanparcel
                GROUP BY  human_humanid, parcel_parcelkey, source_sourceid, linkedobjectrole_lorid,deactivatedts
                HAVING count(*) > 1 AND deactivatedts IS null
        """
    )
    if municode:
        statement = text(
            """
WITH dups AS (
    SELECT array_agg(linkid) linkids, human_humanid, parcel_parcelkey
    FROM humanparcel
    GROUP BY human_humanid, parcel_parcelkey, source_sourceid, linkedobjectrole_lorid, deactivatedts
    HAVING count(*) > 1
       AND deactivatedts IS null
)
    SELECT * FROM dups JOIN parcel p on dups.parcel_parcelkey=p.parcelkey WHERE p.muni_municode=999
    """
    ).params({"municode": municode})
    return conn.execute(statement).all()


# @log_return("Selected duplicate parcel units: {}")
def select_duplicate_parcel_units(conn, municode):
    statement = text(
        """
SELECT array_agg(unitid) unitids, unitnumber, parcel_parcelkey
    FROM parcelunit
    GROUP BY  unitnumber, parcel_parcelkey, deactivatedts
    HAVING count(*) > 1 AND deactivatedts IS null;
        """
    ).params({"municode": municode})
    if municode:
        statement = text(
            """
WITH dups AS (
    SELECT array_agg(unitid) unitids, unitnumber, parcel_parcelkey
    FROM parcelunit
    GROUP BY unitnumber, parcel_parcelkey, deactivatedts
    HAVING count(*) > 1 AND deactivatedts IS null
) SELECT * FROM dups JOIN parcel p on dups.parcel_parcelkey=p.parcelkey WHERE p.muni_municode=999;
            """
    ).params({"municode": municode})
    return  conn.execute(statement).all()


def deactivate_addressid(conn, addressid, log):
    statement = text(
        """
        UPDATE mailingaddress SET deactivatedts=now(), deactivatedby_userid=:user_id WHERE addressid=:address_id; 
        """
    ).params({"address_id": addressid, "user_id": USER_ID})
    conn.execute(statement)
    log.info(f"Deactivated mailingaddress")


def deactivate_parcel(conn, parcelkey):
    statement = text("UPDATE parcel set deactivatedts=now(), deactivatedby_userid=:user_id WHERE parcelkey=:parcelkey").params(
        {"parcelkey": parcelkey, "user_id": USER_ID}
    )
    conn.execute(statement)


def update_human_mailing_address(conn, old, new, log):
    statement = text(
        "UPDATE humanmailingaddress SET humanmailing_addressid=:new, lastupdatedby_userid=:user_id, lastupdatedts=now() WHERE humanmailing_addressid=:old"
        "   RETURNING linkid;"
    ).params({"old": old, "new": new, "user_id": USER_ID})
    linkids = conn.execute(statement).scalars().all()
    if linkids:
        log.info("Updated humanmailingaddress", linkids=linkids)
    else:
        log.info("Updated humanmailingaddress. There were no humanmailingaddresses with the given addressid")

def update_parcelmailingaddress_by_address(conn, old, new, log):
    statement = text(
        "UPDATE parcelmailingaddress SET mailingaddress_addressid=:new, lastupdatedby_userid=:user_id, lastupdatedts=now() WHERE mailingaddress_addressid=:old"
        "   RETURNING linkid"
    ).params({"old": old, "new": new, "user_id": USER_ID})
    address_id = conn.execute(statement).scalars().all()
    if address_id:
        log.info("Updated parcelmailingaddress", address_id=address_id)
    else:
        log.info("Updated parcelmailingaddress. There were no parcelmailingaddresses with the given addressid")


def update_parcelmailingaddress_by_parcel(conn, old, new, log):
    statement = text(
        "UPDATE parcelmailingaddress SET parcel_parcelkey=:new, lastupdatedts=now(), lastupdatedby_userid=:user_id WHERE parcel_parcelkey=:old"
        "   RETURNING parcel_parcelkey"
    ).params({"old": old, "new": new, "user_id": USER_ID})
    parcelkey = conn.execute(statement).scalars().all()
    if parcelkey:
        log.info("Updated parcelmailingaddress", parcelkey=parcelkey)
    else:
        log.info("Updated parcelmailingaddress. There were no parcelmailingaddresses with the given addressid")


def deactivate_parcelmailingaddress_by_link_id(conn, old, log):
    statement = text(
        "UPDATE parcelmailingaddress SET deactivatedts=now(), deactivatedby_userid=:user_id WHERE linkid=:old"
    ).params({"user_id": USER_ID, "old": old})
    conn.execute(statement)
    log.info("Deactivated parcelmailingaddress -------")

def update_parcel_info(conn, old, new, log):
    statement = text(
        "UPDATE parcelinfo SET parcel_parcelkey=:new, lastupdatedby_userid=:user_id, lastupdatedts=now() WHERE parcel_parcelkey=:old"
        "  RETURNING parcelinfoid"
    ).params({"old": old, "new": new, "user_id": USER_ID})
    parcelinfoid = conn.execute(statement).scalars().all()
    if parcelinfoid:
        log.info("Updated parcelinfo", parcelinfoid=parcelinfoid)
    else:
        log.info("Updated parcelinfo. There were no parcelinfos with the given parcelkey")





def update_parcelphotodoc(conn, old, new, log):
    statement = text(
        "UPDATE parcelphotodoc SET parcel_parcelkey=:new WHERE parcel_parcelkey=:old"
        "  RETURNING parcel_parcelkey"
    ).params({"old": old, "new": new})
    parcelkey = conn.execute(statement).scalars().all()
    if parcelkey:
        log.info("Updated parcelphotodoc")
    else:
        log.info("Updated parcelphotodoc. No parcelphotodoc with given parcelkey found.")




def update_parcelunit_by_parcel_key(conn, old, new, log):
    statement = text(
        "UPDATE parcelunit SET parcel_parcelkey=:new, lastupdatedts=now(), lastupdatedby_userid=:user_id WHERE parcel_parcelkey=:old"
        "  RETURNING parcel_parcelkey"
    ).params({"old": old, "new": new, "user_id": USER_ID})
    parcelkey = conn.execute(statement).scalars().all()
    if parcelkey:
        log.info("Updated parcelunit", parcelkey=parcelkey)
    else:
        log.info("Updated parcelunit. There were no parcelunits with the given parcelkey")


def deactivate_parcelunit_by_unit_id(conn, old, log):
    statement = text(
        "UPDATE parcelunit SET deactivatedts=now(), deactivatedby_userid=:user_id WHERE unitid=:old"
    ).params({"old": old, "user_id": USER_ID})
    conn.execute(statement)
    log.info("Deactivated parcel unit -------")



def update_human_parcel_by_parcel(conn, old, new, log):
    statement = text(
        "UPDATE humanparcel SET parcel_parcelkey=:new, lastupdatedby_userid=:user_id, lastupdatedts=now() WHERE parcel_parcelkey=:old"
        "  RETURNING linkid"
    ).params({"old": old, "new": new, "user_id": USER_ID})
    conn.execute(statement)
    log.info("Updated human parcel")


def deactivate_human_parcel_by_linkid(conn, old, log):
    statement = text(
        "UPDATE humanparcel SET deactivatedts=now(), deactivatedby_userid=:user_id WHERE linkid=:old"
        "  RETURNING linkid"
    ).params({"old": old, "user_id": USER_ID})
    conn.execute(statement)
    log.info("Deactivated human parcel -----")

# def update_parcel_unit(conn, unitid, log):
#     statement = text(
#         "UPDATE parcelunit SET deactivatedts=now(), deactivatedby_userid=:user_id WHERE unitid=:unitid"
#     ).params({"unitid": unitid, "user_id": USER_ID})
#     conn.execute(statement)
#     log.info("Deactivated parcelunit -------")


def create_unique_indexes(conn):
    statement = text(
        """
           CREATE UNIQUE INDEX IF NOT EXISTS mailingaddress_unique_where_not_null
                ON mailingaddress (coalesce(bldgno, ''), street_streetid, coalesce(attention, ''), coalesce(secondary, ''))
                WHERE (deactivatedts is null);

            CREATE UNIQUE INDEX IF NOT EXISTS parcel_unique_where_not_null
                ON parcel (parcelidcnty)
                WHERE (deactivatedts is null);

            CREATE UNIQUE INDEX IF NOT EXISTS parcelmailingaddress_unique_where_not_null
                ON parcelmailingaddress (parcel_parcelkey, mailingaddress_addressid, linkedobjectrole_lorid)
                WHERE (deactivatedts is null);
            
            CREATE UNIQUE INDEX IF NOT EXISTS mailingstreet_unique_where_not_null
                ON mailingstreet (name, pobox, citystatezip_cszipid)
                WHERE (deactivatedts is null);
            
            CREATE UNIQUE INDEX IF NOT EXISTS humanparcel_unique_where_not_null
                ON humanparcel (human_humanid, parcel_parcelkey, source_sourceid, linkedobjectrole_lorid)
                WHERE (deactivatedts is null);
            
            
            CREATE UNIQUE INDEX IF NOT EXISTS parcelunit_unique_where_not_null
                on parcelunit (unitnumber, parcel_parcelkey)
                WHERE (deactivatedts is null);
            """
    )
    conn.execute(statement)


def get_munis(conn: Connection):
    statement = text(
        "SELECT municode, muniname FROM municipality;"
    )
    return conn.execute(statement).all()



if __name__ == "__main__":
    global_logger.msg("Starting consolidate.py")
    with get_db_context() as conn:
        for municode, muniname in itertools.chain(get_munis(conn), [(None, "All Municipalities")]):
            log = global_logger.bind(muni=muniname)

            consolidate_mailing_addresses(conn, log, municode=municode)
            consolidate_parcels(conn, log, municode=municode)

            deactivate_duplicate_parcel_mailing_addresses(conn, log, municode=municode)
            deactivate_duplicate_human_parcels(conn, log, municode=municode)
            deactivate_duplicate_parcel_units(conn, log, municode=municode)



        create_unique_indexes(conn)
        # conn.commit()
