from sqlalchemy import Column, String, Integer, Date
from base import Base


class RequestForPermissions(Base):
    __tablename__ = 'requests_for_permissions'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    bot_url = Column(String)
    bot_name = Column(String)
    bot_has_red_link = Column(Integer)
    operator_url = Column(String)
    operator_name = Column(String)
    operator_has_red_link = Column(Integer)
    is_successful = Column(Integer)
    first_edit = Column(Date)
    last_edit = Column(Date)
    closed_at = Column(Date)
    revision_count = Column(Integer)
    editor_count = Column(Integer)
    comment_symbol_count = Column(Integer)
    question_symbol_count = Column(Integer)
    oppose_symbol_count = Column(Integer)
    answer_symbol_count = Column(Integer)
    support_symbol_count = Column(Integer)
    html = Column(String)
    task = Column(String)
    code = Column(String)
    function  = Column(String)
    archive_comment = Column(String)
    summary = Column(String)
    retrieved_at = Column(Date)

    def __init__(self, id, url, bot_url, bot_name, bot_has_red_link, operator_url, operator_name, operator_has_red_link,
                 is_successful, first_edit, last_edit, closed_at, revision_count, editor_count, comment_symbol_count,
                 question_symbol_count, oppose_symbol_count, answer_symbol_count, support_symbol_count, html, task,
                 code, function, archive_comment, summary, retrieved_at):
        self.id = id
        self.url = url
        self.bot_url = bot_url
        self.bot_name = bot_name
        self.bot_has_red_link = bot_has_red_link
        self.operator_url = operator_url
        self.operator_name = operator_name
        self.operator_has_red_link = operator_has_red_link
        self.is_successful = is_successful
        self.first_edit = first_edit
        self.last_edit = last_edit
        self.closed_at = closed_at
        self.revision_count = revision_count
        self.editor_count = editor_count
        self.comment_symbol_count = comment_symbol_count
        self.question_symbol_count = question_symbol_count
        self.oppose_symbol_count = oppose_symbol_count
        self.answer_symbol_count = answer_symbol_count
        self.support_symbol_count = support_symbol_count
        self.html = html
        self.task = task
        self.code = code
        self.function = function
        self.archive_comment = archive_comment
        self.summary = summary
        self.retrieved_at = retrieved_at