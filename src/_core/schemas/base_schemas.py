from pydantic import BaseModel, field_validator

class StripStringsModel(BaseModel):
    @field_validator('*', mode='before')
    @classmethod
    def strip_all_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v