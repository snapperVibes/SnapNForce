""" Schemas representing data from the Allegheny County Real Estate Portal """
from sqlmodel import SQLModel
from bs4 import Tag, NavigableString

class General(SQLModel):
    owner_name: Tag | NavigableString
    address: Tag | NavigableString


class Mortgage(SQLModel):
    mortgage_address: Tag | NavigableString
