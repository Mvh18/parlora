"""Languages and CEFR levels, derived from the domain core rather than duplicated."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from parlora_core.cefr import CefrBand, CefrLevel
from parlora_core.languages import LanguageRegistry

router = APIRouter(tags=["catalogue"])


class LanguageOut(BaseModel):
    code: str = Field(description="ISO 639-1 code.", examples=["en"])
    english_name: str
    native_name: str
    as_target: bool = Field(description="Can be practised in a session.")
    as_feedback: bool = Field(description="Corrections can be explained in it.")


class LanguageList(BaseModel):
    languages: list[LanguageOut]


class CefrLevelOut(BaseModel):
    code: str = Field(examples=["B1"])
    band: CefrBand
    is_beginner: bool = Field(description="A1 and A2: feedback may use the native language.")


class CefrLevelList(BaseModel):
    levels: list[CefrLevelOut] = Field(description="From A1 (lowest) to C2 (highest).")


@router.get("/languages", summary="Supported languages and their roles")
async def languages(request: Request) -> LanguageList:
    registry: LanguageRegistry = request.app.state.language_registry
    return LanguageList(
        languages=[
            LanguageOut(
                code=str(language.code),
                english_name=language.english_name,
                native_name=language.native_name,
                as_target=language.as_target,
                as_feedback=language.as_feedback,
            )
            for language in registry
        ]
    )


@router.get("/cefr-levels", summary="CEFR levels in order")
async def cefr_levels() -> CefrLevelList:
    return CefrLevelList(
        levels=[
            CefrLevelOut(code=level.value, band=level.band, is_beginner=level.is_beginner)
            for level in sorted(CefrLevel)
        ]
    )
