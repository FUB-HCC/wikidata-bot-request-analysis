from sqlalchemy import Column, String, Integer, Date
from base import Base


class Bot(Base):
    __tablename__ = 'bots'

    id = Column(Integer, primary_key=True)
    userid = Column(Integer)
    name = Column(String)
    has_botflag = Column(Integer)
    is_extension_bot = Column(Integer)
    is_blocked = Column(Integer)
    blockid = Column(Integer)
    blockedby = Column(String)
    blockedbyid = Column(Integer)
    blockedtimestamp = Column(Date)
    blockreason = Column(String)
    blockexpiry = Column(String)
    groups = Column(String)
    implicitgroups = Column(String)
    rights = Column(String)
    editcount = Column(Integer)
    registration = Column(String)
    redirect_of = Column(Integer)
    retrieved_at = Column(Date)

    def __init__(self, userid, name, has_botflag, is_extension_bot, is_blocked, blockid, blockedby, blockedbyid, blockedtimestamp, blockreason, blockexpiry, groups, implicitgroups, rights, editcount, registration, redirect_of, retrieved_at):
        self.userid = userid
        self.name = name
        self.has_botflag = has_botflag
        self.is_extension_bot = is_extension_bot
        self.is_blocked = is_blocked
        self.blockid = blockid
        self.blockedby = blockedby
        self.blockedbyid = blockedbyid
        self.blockedtimestamp = blockedtimestamp
        self.blockreason = blockreason
        self.blockexpiry = blockexpiry
        self.groups = groups
        self.implicitgroups = implicitgroups
        self.rights = rights
        self.editcount = editcount
        self.registration = registration
        self.redirect_of = redirect_of
        self.retrieved_at = retrieved_at