"""Project schemas (US-013)"""

import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectBase(BaseModel):
    """Ortak proje alanları"""

    title: str = Field(..., max_length=255, description="Proje adı")
    description: Optional[str] = Field(None, description="Proje açıklaması")
    tech_stack: Optional[List[str]] = Field(None, description="Kullanılan teknolojiler")
    url: Optional[str] = Field(None, max_length=1000, description="Proje bağlantısı")


class ProjectCreate(ProjectBase):
    """Yeni proje oluşturma"""

    pass


class ProjectUpdate(BaseModel):
    """Proje güncelleme (kısmi)"""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    url: Optional[str] = Field(None, max_length=1000)


class ProjectResponse(ProjectBase):
    """Proje yanıtı"""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tech_stack", mode="before")
    @classmethod
    def parse_tech_stack(cls, v):
        """DB'de tech_stack Text(JSON string) olarak tutulur, API'de List[str] döner"""
        if isinstance(v, str):
            return json.loads(v) if v else []
        return v
