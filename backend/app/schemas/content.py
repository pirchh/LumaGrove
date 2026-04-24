from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.core.time import serialize_utc


class UTCModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at_utc", "updated_at_utc", "published_at_utc", check_fields=False)
    def serialize_datetime_fields(self, value: datetime | None) -> str | None:
        return serialize_utc(value)


class AssetRead(UTCModel):
    id: UUID
    original_filename: str
    stored_filename: str
    storage_path: str
    public_url: str
    mime_type: str
    size_bytes: int
    sha256: str
    created_at_utc: datetime | None = None
    updated_at_utc: datetime | None = None


class TaxonomyRead(UTCModel):
    id: UUID
    name: str
    slug: str
    description: str | None = None
    created_at_utc: datetime | None = None
    updated_at_utc: datetime | None = None


class TaxonomyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: str | None = Field(default=None, max_length=100)
    description: str | None = None


class PlantBase(BaseModel):
    common_name: str = Field(min_length=1, max_length=160)
    latin_name: str | None = Field(default=None, max_length=160)
    slug: str | None = Field(default=None, max_length=180)
    summary: str | None = None
    origin_region: str | None = Field(default=None, max_length=160)
    growth_zones: str | None = Field(default=None, max_length=160)
    light_preference: str | None = Field(default=None, max_length=200)
    water_preference: str | None = Field(default=None, max_length=200)
    humidity_preference: str | None = Field(default=None, max_length=200)
    temperature_range: str | None = Field(default=None, max_length=200)
    soil_preference: str | None = Field(default=None, max_length=200)
    growth_habit: str | None = Field(default=None, max_length=200)
    edible: bool = False
    indoor_friendly: bool = True
    flowering: bool = False
    notes: str | None = None
    cover_image_url: str | None = None
    growth_range_image_url: str | None = None
    cover_asset_id: UUID | None = None
    growth_range_asset_id: UUID | None = None
    is_public: bool = True
    category_slugs: list[str] = []
    tag_slugs: list[str] = []


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseModel):
    common_name: str | None = Field(default=None, max_length=160)
    latin_name: str | None = Field(default=None, max_length=160)
    slug: str | None = Field(default=None, max_length=180)
    summary: str | None = None
    origin_region: str | None = Field(default=None, max_length=160)
    growth_zones: str | None = Field(default=None, max_length=160)
    light_preference: str | None = Field(default=None, max_length=200)
    water_preference: str | None = Field(default=None, max_length=200)
    humidity_preference: str | None = Field(default=None, max_length=200)
    temperature_range: str | None = Field(default=None, max_length=200)
    soil_preference: str | None = Field(default=None, max_length=200)
    growth_habit: str | None = Field(default=None, max_length=200)
    edible: bool | None = None
    indoor_friendly: bool | None = None
    flowering: bool | None = None
    notes: str | None = None
    cover_image_url: str | None = None
    growth_range_image_url: str | None = None
    cover_asset_id: UUID | None = None
    growth_range_asset_id: UUID | None = None
    is_public: bool | None = None
    category_slugs: list[str] | None = None
    tag_slugs: list[str] | None = None


class PlantRead(UTCModel):
    id: UUID
    common_name: str
    latin_name: str | None
    slug: str
    summary: str | None
    origin_region: str | None
    growth_zones: str | None
    light_preference: str | None
    water_preference: str | None
    humidity_preference: str | None
    temperature_range: str | None
    soil_preference: str | None
    growth_habit: str | None
    edible: bool
    indoor_friendly: bool
    flowering: bool
    notes: str | None
    cover_image_url: str | None
    growth_range_image_url: str | None
    cover_asset_id: UUID | None = None
    growth_range_asset_id: UUID | None = None
    cover_asset: AssetRead | None = None
    growth_range_asset: AssetRead | None = None
    is_public: bool
    categories: list[TaxonomyRead] = []
    tags: list[TaxonomyRead] = []
    created_at_utc: datetime | None = None
    updated_at_utc: datetime | None = None


class ArticleSectionBase(BaseModel):
    title: str = Field(min_length=1, max_length=220)
    body: str = Field(min_length=1)
    section_date: date | None = None
    sort_order: int = 0
    anchor_slug: str | None = Field(default=None, max_length=180)
    image_url: str | None = None
    asset_id: UUID | None = None


class ArticleSectionCreate(ArticleSectionBase):
    pass


class ArticleSectionUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=220)
    body: str | None = None
    section_date: date | None = None
    sort_order: int | None = None
    anchor_slug: str | None = Field(default=None, max_length=180)
    image_url: str | None = None
    asset_id: UUID | None = None


class ArticleSectionRead(UTCModel):
    id: UUID
    article_id: UUID
    title: str
    body: str
    section_date: date | None
    sort_order: int
    anchor_slug: str
    image_url: str | None
    asset_id: UUID | None = None
    asset: AssetRead | None = None
    created_at_utc: datetime | None = None
    updated_at_utc: datetime | None = None


class ArticleBase(BaseModel):
    plant_id: UUID | None = None
    title: str = Field(min_length=1, max_length=220)
    slug: str | None = Field(default=None, max_length=240)
    article_type: str = Field(default="article", min_length=1, max_length=40)
    summary: str | None = None
    cover_image_url: str | None = None
    cover_asset_id: UUID | None = None
    published_at_utc: datetime | None = None
    start_date: date | None = None
    is_public: bool = True
    category_slugs: list[str] = []
    tag_slugs: list[str] = []
    sections: list[ArticleSectionCreate] = []


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    plant_id: UUID | None = None
    title: str | None = Field(default=None, max_length=220)
    slug: str | None = Field(default=None, max_length=240)
    article_type: str | None = Field(default=None, max_length=40)
    summary: str | None = None
    cover_image_url: str | None = None
    cover_asset_id: UUID | None = None
    published_at_utc: datetime | None = None
    start_date: date | None = None
    is_public: bool | None = None
    category_slugs: list[str] | None = None
    tag_slugs: list[str] | None = None


class ArticleRead(UTCModel):
    id: UUID
    plant_id: UUID | None
    title: str
    slug: str
    article_type: str
    summary: str | None
    cover_image_url: str | None
    cover_asset_id: UUID | None = None
    cover_asset: AssetRead | None = None
    published_at_utc: datetime | None
    start_date: date | None
    is_public: bool
    plant: PlantRead | None = None
    categories: list[TaxonomyRead] = []
    tags: list[TaxonomyRead] = []
    sections: list[ArticleSectionRead] = []
    created_at_utc: datetime | None = None
    updated_at_utc: datetime | None = None


class ArticleListResponse(BaseModel):
    items: list[ArticleRead]
    count: int


class PlantListResponse(BaseModel):
    items: list[PlantRead]
    count: int
