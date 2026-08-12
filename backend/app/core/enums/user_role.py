from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    TEACHING_ASSISTANT = "teaching_assistant"
    STUDENT = "student"