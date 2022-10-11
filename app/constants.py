from collections import namedtuple

_AddressAndHumanRoles = namedtuple("AddressAndAddresseeRoles", ["address", "human"])
_GeneralAndMortgageRoles = namedtuple("GeneralAndMortgageRoles", ["general", "mortgage"])

import warnings

warnings.warn("LINKED OBJECT ROLES AREN'T CORRECT: 237 is a duplicate of 116 (currently owns)")


class LinkedObjectRole:
    IS_ASSOCIATED_WITH = 101

    GENERAL_HUMAN_MAILING_ADDRESS = 103
    OWNER_NAME = 237

    MORTGAGE_HUMAN_MAILING_ADDRESS = 234
    MORTGAGE_ADDRESSEE = 236
    COUNTY_PROPERTY_ADDRESS = 235

    CURRENT_OWNER = 116
    FORMER_OWNER = 117

    CURRENT_TAX_ADDRESSEE = 0
    FORMER_TAX_ADDRESSEE = 0



    @classmethod
    @property
    def cogland(cls):
        return 999

    @classmethod
    @property
    def general_roles(cls):
        return _AddressAndHumanRoles(cls.GENERAL_HUMAN_MAILING_ADDRESS, cls.OWNER_NAME)

    @classmethod
    @property
    def mortgage_roles(cls):
        return _AddressAndHumanRoles(cls.MORTGAGE_HUMAN_MAILING_ADDRESS, cls.MORTGAGE_ADDRESSEE)

    @classmethod
    @property
    def address_roles(cls):
        return _GeneralAndMortgageRoles(
            cls.GENERAL_HUMAN_MAILING_ADDRESS, cls.MORTGAGE_HUMAN_MAILING_ADDRESS
        )

    @classmethod
    @property
    def addressee_roles(cls):
        return _GeneralAndMortgageRoles(cls.OWNER_NAME, cls.MORTGAGE_ADDRESSEE)

    @classmethod
    @property
    def property_address_roles(cls):
        return (cls.COUNTY_PROPERTY_ADDRESS,)


USER_ID = 99  # the id of "sylvia". Todo: new user id
SOURCE_ID = None  # Todo: new source id
COGLAND_MUNICODE = 999