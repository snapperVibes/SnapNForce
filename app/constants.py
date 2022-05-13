from collections import namedtuple

_AddressAndHumanRoles = namedtuple("AddressAndAddresseeRoles", ["address", "human"])
_GeneralAndMortgageRoles = namedtuple("GeneralAndMortgageRoles", ["general", "mortgage"])


class LinkedObjectRole:
    GENERAL_HUMAN_MAILING_ADDRESS = 103
    GENERAL_HUMAN = 237
    MORTGAGE_HUMAN_MAILING_ADDRESS = 234
    MORTGAGE_HUMAN = 236
    COUNTY_PROPERTY_ADDRESS = 235

    @classmethod
    @property
    def general_roles(cls):
        return _AddressAndHumanRoles(cls.GENERAL_HUMAN_MAILING_ADDRESS, cls.GENERAL_HUMAN)

    @classmethod
    @property
    def mortgage_roles(cls):
        return _AddressAndHumanRoles(cls.MORTGAGE_HUMAN_MAILING_ADDRESS, cls.MORTGAGE_HUMAN)

    @classmethod
    @property
    def address_roles(cls):
        return _GeneralAndMortgageRoles(cls.GENERAL_HUMAN_MAILING_ADDRESS, cls.MORTGAGE_HUMAN_MAILING_ADDRESS)

    @classmethod
    @property
    def addressee_roles(cls):
        return _GeneralAndMortgageRoles(cls.GENERAL_HUMAN, cls.MORTGAGE_HUMAN)

    @classmethod
    @property
    def property_address_roles(cls):
        return cls.COUNTY_PROPERTY_ADDRESS,


USER_ID = 99  # the id of "sylvia". Todo: new user id
