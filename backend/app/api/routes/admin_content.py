from __future__ import annotations

import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    Article,
    ArticleCategory,
    ArticleSection,
    ArticleTag,
    Category,
    Plant,
    PlantCategory,
    PlantTag,
    Tag,
)
from app.db.session import get_db
from app.schemas.content import (
    ArticleCreate,
    ArticleListResponse,
    ArticleRead,
    ArticleSectionCreate,
    ArticleSectionRead,
    ArticleUpdate,
    PlantCreate,
    PlantListResponse,
    PlantRead,
    PlantUpdate,
    TaxonomyCreate,
    TaxonomyRead,
)
from app.api.routes.public_content import _hydrate_article, _hydrate_plant, ARTICLE_LOAD, PLANT_LOAD

router = APIRouter(prefix="/admin/content", tags=["admin-content"])


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def get_or_create_category(db: Session, slug: str) -> Category:
    category = db.scalar(select(Category).where(Category.slug == slug))
    if category is not None:
        return category
    category = Category(name=slug.replace("-", " ").title(), slug=slug)
    db.add(category)
    db.flush()
    return category


def get_or_create_tag(db: Session, slug: str) -> Tag:
    tag = db.scalar(select(Tag).where(Tag.slug == slug))
    if tag is not None:
        return tag
    tag = Tag(name=slug.replace("-", " ").title(), slug=slug)
    db.add(tag)
    db.flush()
    return tag


def sync_plant_taxonomy(db: Session, plant: Plant, category_slugs: list[str] | None, tag_slugs: list[str] | None) -> None:
    if category_slugs is not None:
        plant.category_links.clear()
        db.flush()
        for index, raw_slug in enumerate(category_slugs):
            category = get_or_create_category(db, slugify(raw_slug))
            plant.category_links.append(PlantCategory(category=category, sort_order=index))
    if tag_slugs is not None:
        plant.tag_links.clear()
        db.flush()
        for index, raw_slug in enumerate(tag_slugs):
            tag = get_or_create_tag(db, slugify(raw_slug))
            plant.tag_links.append(PlantTag(tag=tag, sort_order=index))


def sync_article_taxonomy(db: Session, article: Article, category_slugs: list[str] | None, tag_slugs: list[str] | None) -> None:
    if category_slugs is not None:
        article.category_links.clear()
        db.flush()
        for index, raw_slug in enumerate(category_slugs):
            category = get_or_create_category(db, slugify(raw_slug))
            article.category_links.append(ArticleCategory(category=category, sort_order=index))
    if tag_slugs is not None:
        article.tag_links.clear()
        db.flush()
        for index, raw_slug in enumerate(tag_slugs):
            tag = get_or_create_tag(db, slugify(raw_slug))
            article.tag_links.append(ArticleTag(tag=tag, sort_order=index))


@router.post("/categories", response_model=TaxonomyRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: TaxonomyCreate, db: Session = Depends(get_db)) -> TaxonomyRead:
    category = Category(name=payload.name, slug=slugify(payload.slug or payload.name), description=payload.description)
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists.") from exc
    db.refresh(category)
    return TaxonomyRead.model_validate(category)


@router.post("/tags", response_model=TaxonomyRead, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TaxonomyCreate, db: Session = Depends(get_db)) -> TaxonomyRead:
    tag = Tag(name=payload.name, slug=slugify(payload.slug or payload.name), description=payload.description)
    db.add(tag)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists.") from exc
    db.refresh(tag)
    return TaxonomyRead.model_validate(tag)


@router.post("/plants", response_model=PlantRead, status_code=status.HTTP_201_CREATED)
def create_plant(payload: PlantCreate, db: Session = Depends(get_db)) -> PlantRead:
    plant = Plant(
        common_name=payload.common_name,
        latin_name=payload.latin_name,
        slug=slugify(payload.slug or payload.common_name),
        summary=payload.summary,
        origin_region=payload.origin_region,
        growth_zones=payload.growth_zones,
        light_preference=payload.light_preference,
        water_preference=payload.water_preference,
        humidity_preference=payload.humidity_preference,
        temperature_range=payload.temperature_range,
        soil_preference=payload.soil_preference,
        growth_habit=payload.growth_habit,
        edible=payload.edible,
        indoor_friendly=payload.indoor_friendly,
        flowering=payload.flowering,
        notes=payload.notes,
        cover_image_url=payload.cover_image_url,
        growth_range_image_url=payload.growth_range_image_url,
        cover_asset_id=payload.cover_asset_id,
        growth_range_asset_id=payload.growth_range_asset_id,
        is_public=payload.is_public,
    )
    db.add(plant)
    db.flush()
    sync_plant_taxonomy(db, plant, payload.category_slugs, payload.tag_slugs)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Plant slug already exists.") from exc
    db.refresh(plant)
    plant = db.scalar(select(Plant).where(Plant.id == plant.id).options(*PLANT_LOAD))
    return _hydrate_plant(plant)


@router.get("/plants", response_model=PlantListResponse)
def list_admin_plants(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)) -> PlantListResponse:
    plants = list(db.scalars(select(Plant).options(*PLANT_LOAD).order_by(Plant.created_at_utc.desc()).limit(limit)).all())
    return PlantListResponse(items=[_hydrate_plant(plant) for plant in plants], count=len(plants))


@router.patch("/plants/{plant_id}", response_model=PlantRead)
def update_plant(plant_id: UUID, payload: PlantUpdate, db: Session = Depends(get_db)) -> PlantRead:
    plant = db.scalar(select(Plant).where(Plant.id == plant_id).options(*PLANT_LOAD))
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found.")
    data = payload.model_dump(exclude_unset=True)
    category_slugs = data.pop("category_slugs", None)
    tag_slugs = data.pop("tag_slugs", None)
    for key, value in data.items():
        if key == "slug" and value is not None:
            value = slugify(value)
        setattr(plant, key, value)
    sync_plant_taxonomy(db, plant, category_slugs, tag_slugs)
    db.commit()
    plant = db.scalar(select(Plant).where(Plant.id == plant_id).options(*PLANT_LOAD))
    return _hydrate_plant(plant)


@router.post("/articles", response_model=ArticleRead, status_code=status.HTTP_201_CREATED)
def create_article(payload: ArticleCreate, db: Session = Depends(get_db)) -> ArticleRead:
    article = Article(
        plant_id=payload.plant_id,
        title=payload.title,
        slug=slugify(payload.slug or payload.title),
        article_type=payload.article_type,
        summary=payload.summary,
        cover_image_url=payload.cover_image_url,
        cover_asset_id=payload.cover_asset_id,
        published_at_utc=payload.published_at_utc,
        start_date=payload.start_date,
        is_public=payload.is_public,
    )
    db.add(article)
    db.flush()
    sync_article_taxonomy(db, article, payload.category_slugs, payload.tag_slugs)
    for index, section_payload in enumerate(payload.sections):
        section = ArticleSection(
            article=article,
            title=section_payload.title,
            body=section_payload.body,
            section_date=section_payload.section_date,
            sort_order=section_payload.sort_order if section_payload.sort_order is not None else index,
            anchor_slug=slugify(section_payload.anchor_slug or section_payload.title),
            image_url=section_payload.image_url,
            asset_id=section_payload.asset_id,
        )
        db.add(section)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Article slug or section anchor already exists.") from exc
    article = db.scalar(select(Article).where(Article.id == article.id).options(*ARTICLE_LOAD))
    return _hydrate_article(article)


@router.get("/articles", response_model=ArticleListResponse)
def list_admin_articles(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)) -> ArticleListResponse:
    articles = list(db.scalars(select(Article).options(*ARTICLE_LOAD).order_by(Article.created_at_utc.desc()).limit(limit)).all())
    return ArticleListResponse(items=[_hydrate_article(article) for article in articles], count=len(articles))


@router.patch("/articles/{article_id}", response_model=ArticleRead)
def update_article(article_id: UUID, payload: ArticleUpdate, db: Session = Depends(get_db)) -> ArticleRead:
    article = db.scalar(select(Article).where(Article.id == article_id).options(*ARTICLE_LOAD))
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    data = payload.model_dump(exclude_unset=True)
    category_slugs = data.pop("category_slugs", None)
    tag_slugs = data.pop("tag_slugs", None)
    for key, value in data.items():
        if key == "slug" and value is not None:
            value = slugify(value)
        setattr(article, key, value)
    sync_article_taxonomy(db, article, category_slugs, tag_slugs)
    db.commit()
    article = db.scalar(select(Article).where(Article.id == article_id).options(*ARTICLE_LOAD))
    return _hydrate_article(article)


@router.post("/articles/{article_id}/sections", response_model=ArticleSectionRead, status_code=status.HTTP_201_CREATED)
def create_article_section(article_id: UUID, payload: ArticleSectionCreate, db: Session = Depends(get_db)) -> ArticleSectionRead:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    section = ArticleSection(
        article_id=article_id,
        title=payload.title,
        body=payload.body,
        section_date=payload.section_date,
        sort_order=payload.sort_order,
        anchor_slug=slugify(payload.anchor_slug or payload.title),
        image_url=payload.image_url,
        asset_id=payload.asset_id,
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return ArticleSectionRead.model_validate(section)
