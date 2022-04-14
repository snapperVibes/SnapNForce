import app
from app.lib import get_tax_data, OwnerData, MailingData, MailingAddress
from app.database import get_db
from sqlalchemy import text
from sqlalchemy.engine import Connection

from lib import scrape, parse


def get_parcel_ids(conn: Connection):
    cursor_result = conn.execute(text("SELECT parcelidcnty FROM parcel WHERE deactivatedts IS NULL LIMIT 300;"))
    return [i[0] for i in cursor_result]


SKIP_TO = 0

if __name__ == '__main__':
    with get_db() as conn:
        parcel_ids = get_parcel_ids(conn)

    with open("out3.txt", "w") as f:
        for i, parcel_id in enumerate(parcel_ids):
            if i < SKIP_TO:
                continue
            # tax = get_tax_data(parcel_id)
            response = scrape.tax_info(parcel_id)
            response.raise_for_status()
            _owner, _mailing = parse.tax_content(response.content)
            owner_data = OwnerData.from_raw(_owner)
            mailing_data = MailingData.from_raw_tax(_mailing)
            tax = MailingAddress(owner_data, mailing_data)

            f.write(f"{owner_data}\n")
            f.write(f"{_mailing}\n")
            f.write(f"{mailing_data}\n")
            f.write(f"{'-' * 89}\n\n")

            print(i, tax, sep="\t")




