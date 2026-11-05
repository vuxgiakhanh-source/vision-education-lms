from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClassInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=200)

    @field_validator('title', mode='before')
    @classmethod
    def normalize_title(cls, value):
        return value.strip() if isinstance(value, str) else value


class ClassOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    teacher_id: int
