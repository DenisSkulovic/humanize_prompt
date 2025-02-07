from pydantic import BaseModel, Field

class ExplanationDTO(BaseModel):
    """
    DTO for explanation version management.
    """
    version_number: float = Field(..., description="Version number of the explanation settings")
    text: str = Field(..., description="Explanation text to be used for humanization")

    @staticmethod
    def build(version_number: float, text: str):
        return ExplanationDTO(version_number=version_number, text=text)
