"""Work experience schemas (US-013)"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkExperienceBase(BaseModel):
    """Ortak iş deneyimi alanları"""

    company: str = Field(..., max_length=255, description="Şirket adı")
    title: str = Field(..., max_length=255, description="Pozisyon / unvan")
    start_date: Optional[date] = Field(None, description="Başlangıç tarihi")
    end_date: Optional[date] = Field(None, description="Bitiş tarihi (devam ediyorsa boş)")
    description: Optional[str] = Field(None, description="Açıklama")


class WorkExperienceCreate(WorkExperienceBase):
    """Yeni iş deneyimi oluşturma"""

    pass


class WorkExperienceUpdate(BaseModel):
    """İş deneyimi güncelleme (kısmi)"""

    company: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class WorkExperienceResponse(WorkExperienceBase):
    """İş deneyimi yanıtı"""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
