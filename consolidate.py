"""
One off script to add a database integrity check to ensure
multiple mailingaddress referring to the same building cannot be active at the same time
"""
from os import path

from sqlalchemy import text
from sqlalchemy.engine import Connection
from app.database import get_db_context
# from constants._common import USER_ID

import logging
logging.basicConfig(filename=path.join("log", "consolidate.log"))

def select_duplicate_address_ids(conn: Connection):
    statement = text(
        """
        -- SELECT bldgno, street_streetid, attention, secondary, array_agg(addressid) addressids FROM mailingaddress
        SELECT array_agg(addressid) addressids FROM mailingaddress
            GROUP BY bldgno, street_streetid, attention, secondary, deactivatedts
            HAVING count(*) > 1 AND deactivatedts IS null
            -- ORDER BY createdts DESC;
        """
    )
    return conn.execute(statement).scalars()

def select_duplicate_parcel_keys(conn):
    statement = text(
        """
        SELECT array_agg(parcelkey) parcelkeys FROM parcel
            GROUP BY parcelidcnty, deactivatedts
            HAVING count(*) > 1 AND deactivatedts IS null
        """
    )
    return conn.execute(statement).scalars()


def select_duplicate_parcel_mailing_addresses(conn):
    statement = text(
        """
        SELECT array_agg(linkid) linkids FROM parcelmailingaddress
            GROUP BY parcel_parcelkey, mailingaddress_addressid, deactivatedts
            HAVING count(*) > 1 AND deactivatedts IS null
        """
    )
    out =  conn.execute(statement).scalars()
    return out


def deactivate_addressid(conn, addressid):
    statement = text(
        """
        UPDATE mailingaddress SET deactivatedts=now() WHERE addressid=:address_id; 
        """
    ).params({"address_id": addressid})
    conn.execute(statement)


def deactivate_parcel(conn, parcelkey):
    statement = text("UPDATE parcel set deactivatedts=now() WHERE parcelkey=:parcelkey").params({"parcelkey": parcelkey})
    conn.execute(statement)


def update_human_mailing_address(conn, old, new):
    statement = text(
        "UPDATE humanmailingaddress SET humanmailing_addressid=:new WHERE humanmailing_addressid=:old;"
    ).params({"old": old, "new": new})
    conn.execute(statement)


def update_parcelmailingaddress(conn, old, new):
    statement = text(
        "UPDATE parcelmailingaddress SET mailingaddress_addressid=:new WHERE mailingaddress_addressid=:old"
    ).params({"old": old, "new": new})
    conn.execute(statement)


def consolidate_mailing_addresses(conn: Connection):
    global f
    f.write("MAILING ADDRESSES:\n")
    for address_ids in select_duplicate_address_ids(conn):
        truth: int = address_ids[0]
        dups: list[int] = address_ids[1:]

        f.write(f"\tTRUTH:\t{truth}\n\tDUPS:\t{dups}\n")
        for addressid in dups:
            deactivate_addressid(conn, addressid)
            update_human_mailing_address(conn, old=addressid, new=truth)
            update_parcelmailingaddress(conn, old=addressid, new=truth)


def update_human_parcel(conn, old, new):
    statement = text(
        "UPDATE humanparcel SET parcel_parcelkey=:new WHERE parcel_parcelkey=:old"
    ).params({"old": old, "new": new})
    conn.execute(statement)

def update_parcel_info(conn, old, new):
    statement = text(
        "UPDATE parcelinfo SET parcel_parcelkey=:new WHERE parcel_parcelkey=:old"
    ).params({"old": old, "new": new})
    conn.execute(statement)


def update_parcelpdfdoc(conn, old, new):
    statement = text(
        "UPDATE parcelpdfdoc SET parcel_parcelkey=:new WHERE parcel_parcelkey=:old"
    ).params({"old": old, "new": new})
    conn.execute(statement)

def update_parcelphotodoc(conn, old, new):
    statement = text(
        "UPDATE parcelphotodoc SET parcel_parcelkey=:new WHERE parcel_parcelkey=:old"
    ).params({"old": old, "new": new})
    conn.execute(statement)

def update_parcelunit(conn, old, new):
    statement = text(
        "UPDATE parcelunit SET parcel_parcelkey=:new WHERE parcel_parcelkey=:old"
    ).params({"old": old, "new": new})
    conn.execute(statement)





def consolidate_parcels(conn: Connection):
    global f
    f.write("PARCELS:\n")
    for parcel_keys in select_duplicate_parcel_keys(conn):
        truth: int = parcel_keys[0]
        dups: list[int] = parcel_keys[1:]
        f.write(f"\tTRUTH:\t{truth}\n\tDUPS:\t{dups}\n")
        for parcel_key in dups:
            deactivate_parcel(conn, parcel_key)
            update_functions = [
                update_parcelmailingaddress,
                update_human_parcel,
                update_parcel_info,
                update_parcelpdfdoc,
                update_parcelphotodoc,
                update_parcelunit
            ]
            for func in update_functions:
                func(conn, old=parcel_key, new=truth)


def deactivate_parcel_mailing_address(conn, linkid):
    statement = text(
        "UPDATE parcelmailingaddress SET deactivatedts=now() WHERE linkid=:linkid"
    ).params({"linkid": linkid})
    conn.execute(statement)


def consolidate_parcel_mailing_addresses(conn: Connection):
    global f
    f.write("PARCEL MAILING ADDRESSES:\n")
    for linkids in select_duplicate_parcel_mailing_addresses(conn):
        truth = linkids[0]
        dups: list[int] = linkids[1:]
        f.write(f"\tTRUTH:\t{truth}\n\tDUPS:\t{dups}\n")
        for linkid in dups:
            deactivate_parcel_mailing_address(conn, linkid)


def create_unique_indexes(conn):
    statement = text(
            """
           CREATE UNIQUE INDEX IF NOT EXISTS mailingaddress_unique_where_not_null
                ON mailingaddress (bldgno, attention, secondary)
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

            """
        )
    conn.execute(statement)








if __name__ == "__main__":
    with get_db_context() as conn:
        with conn.begin():
            with open("yooo.txt", "w") as f:
                consolidate_mailing_addresses(conn)
                consolidate_parcels(conn)
                consolidate_parcel_mailing_addresses(conn)
                create_unique_indexes(conn)