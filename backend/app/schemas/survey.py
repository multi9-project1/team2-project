from typing import Optional
from pydantic import BaseModel

class SurveyInputModel(BaseModel):
    gender: Optional[str] = "U"
    personal_color: Optional[str] = "unknown"
    Q1: Optional[str] = None
    Q2: Optional[str] = None
    Q3: Optional[str] = None
    Qwarm: Optional[str] = None
    Qcool: Optional[str] = None
    Qstyle_1: Optional[str] = None
    Qstyle_2: Optional[str] = None
    Qstyle_3: Optional[str] = None
    Qstyle_4: Optional[str] = None
    Qstyle_5: Optional[str] = None
    Qstyle_6: Optional[str] = None
    Qstyle_7: Optional[str] = None
    Qstyle_8: Optional[str] = None
    Qstyle_9: Optional[str] = None