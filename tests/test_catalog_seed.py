from pathlib import Path

from app import app
from catalog_seed import seed_catalog
from extensions import db
from models import Product, Recipe


def test_catalog_is_complete_local_and_idempotent():
    with app.app_context():
        product_count = Product.query.count()
        recipe_count = Recipe.query.count()
        assert product_count >= 50
        assert recipe_count >= 30

        for product in Product.query.all():
            assert product.image.startswith('/static/img/products/')
            assert (Path(app.root_path) / product.image.lstrip('/').replace('/', '\\')).is_file()

        for recipe in Recipe.query.all():
            assert recipe.ingredients.count('\n') >= 4
            assert recipe.instructions.count('\n') >= 4
            assert recipe.prep_time
            assert recipe.servings > 0
            assert recipe.difficulty in {'Fácil', 'Media', 'Difícil'}

        seed_catalog()
        assert Product.query.count() == product_count
        assert Recipe.query.count() == recipe_count


def test_recipe_listing_and_detail_pages():
    client = app.test_client()
    listing = client.get('/recipes')
    assert listing.status_code == 200
    assert b'Galletas caseras' in listing.data
    assert b'Ver receta completa' in listing.data

    with app.app_context():
        recipe_id = Recipe.query.order_by(Recipe.id).first().id
    detail = client.get(f'/recipes/{recipe_id}')
    assert detail.status_code == 200
    assert b'Ingredientes' in detail.data
    assert b'Preparaci' in detail.data


def test_catalog_product_image_is_served_locally():
    client = app.test_client()
    with app.app_context():
        image_urls = {product.image for product in Product.query.all()}
    for image_url in image_urls:
        response = client.get(image_url)
        assert response.status_code == 200
        assert response.mimetype == 'image/svg+xml'

    catalog_page = client.get('/products')
    assert catalog_page.status_code == 200
    assert b'/static/img/products/' in catalog_page.data
