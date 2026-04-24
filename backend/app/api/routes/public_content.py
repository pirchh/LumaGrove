from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Article, ArticleCategory, ArticleSection, ArticleTag, Plant, PlantCategory, PlantTag
from app.db.session import get_db
from app.schemas.content import ArticleListResponse, ArticleRead, PlantListResponse, PlantRead

router = APIRouter(prefix="/public", tags=["public-content"])

ARTICLE_LOAD = (
    selectinload(Article.cover_asset),
    selectinload(Article.plant).selectinload(Plant.cover_asset),
    selectinload(Article.plant).selectinload(Plant.growth_range_asset),
    selectinload(Article.plant).selectinload(Plant.category_links).selectinload(PlantCategory.category),
    selectinload(Article.plant).selectinload(Plant.tag_links).selectinload(PlantTag.tag),
    selectinload(Article.sections).selectinload(ArticleSection.asset),
    selectinload(Article.category_links).selectinload(ArticleCategory.category),
    selectinload(Article.tag_links).selectinload(ArticleTag.tag),
)

PLANT_LOAD = (
    selectinload(Plant.cover_asset),
    selectinload(Plant.growth_range_asset),
    selectinload(Plant.category_links).selectinload(PlantCategory.category),
    selectinload(Plant.tag_links).selectinload(PlantTag.tag),
)


def _hydrate_plant(plant: Plant) -> PlantRead:
    data = PlantRead.model_validate(plant).model_dump()
    data["categories"] = [link.category for link in sorted(plant.category_links, key=lambda item: item.sort_order)]
    data["tags"] = [link.tag for link in sorted(plant.tag_links, key=lambda item: item.sort_order)]
    if plant.cover_asset is not None:
        data["cover_asset"] = plant.cover_asset
        data["cover_image_url"] = plant.cover_asset.public_url
    if plant.growth_range_asset is not None:
        data["growth_range_asset"] = plant.growth_range_asset
        data["growth_range_image_url"] = plant.growth_range_asset.public_url
    return PlantRead.model_validate(data)


def _hydrate_article(article: Article) -> ArticleRead:
    data = ArticleRead.model_validate(article).model_dump()
    data["categories"] = [link.category for link in sorted(article.category_links, key=lambda item: item.sort_order)]
    data["tags"] = [link.tag for link in sorted(article.tag_links, key=lambda item: item.sort_order)]
    sections = sorted(article.sections, key=lambda section: section.sort_order)
    section_payloads = []
    for section in sections:
        section_data = section.__dict__.copy()
        if section.asset is not None:
            section_data["asset"] = section.asset
            section_data["image_url"] = section.asset.public_url
        section_payloads.append(section_data)
    data["sections"] = section_payloads
    if article.cover_asset is not None:
        data["cover_asset"] = article.cover_asset
        data["cover_image_url"] = article.cover_asset.public_url
    if article.plant is not None:
        data["plant"] = _hydrate_plant(article.plant)
    return ArticleRead.model_validate(data)


@router.get("/articles", response_model=ArticleListResponse)
def list_public_articles(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)) -> ArticleListResponse:
    stmt = (
        select(Article)
        .where(Article.is_public.is_(True))
        .options(*ARTICLE_LOAD)
        .order_by(Article.published_at_utc.desc().nullslast(), Article.created_at_utc.desc())
        .limit(limit)
    )
    articles = list(db.scalars(stmt).all())
    return ArticleListResponse(items=[_hydrate_article(article) for article in articles], count=len(articles))


@router.get("/articles/{slug}", response_model=ArticleRead)
def get_public_article(slug: str, db: Session = Depends(get_db)) -> ArticleRead:
    stmt = select(Article).where(Article.slug == slug, Article.is_public.is_(True)).options(*ARTICLE_LOAD)
    article = db.scalar(stmt)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    return _hydrate_article(article)


@router.get("/plants", response_model=PlantListResponse)
def list_public_plants(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)) -> PlantListResponse:
    stmt = select(Plant).where(Plant.is_public.is_(True)).options(*PLANT_LOAD).order_by(Plant.common_name.asc()).limit(limit)
    plants = list(db.scalars(stmt).all())
    return PlantListResponse(items=[_hydrate_plant(plant) for plant in plants], count=len(plants))


@router.get("/plants/{slug}", response_model=PlantRead)
def get_public_plant(slug: str, db: Session = Depends(get_db)) -> PlantRead:
    stmt = select(Plant).where(Plant.slug == slug, Plant.is_public.is_(True)).options(*PLANT_LOAD)
    plant = db.scalar(stmt)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found.")
    return _hydrate_plant(plant)
