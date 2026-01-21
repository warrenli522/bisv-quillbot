from enum import Enum

class ArticleStatus(Enum):
    """Status of a given article"""
    DRAFT = "Draft"
    SECTION = "Section Edits"
    SECTION_REVISE = "Section Edit Revision"
    EIC = "EIC Edits"
    EIC_REVISE = "EIC Edit Revision"
    SHAPIRO_EDIT = "Shapiro Edit"
    SHAPIRO_REVISE = "Shapiro Edit Revision"
    PUBLISHED = "Published"
