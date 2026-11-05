from flask import Flask, redirect, render_template, session, url_for

from config import Config
from catalog_seed import migrate_recipe_difficulty, seed_catalog
from extensions import csrf, db, login_manager
from models import Category, PremiumPlan, Product, Recipe, Review, User
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.cart import cart_bp
from routes.main import main_bp
from routes.orders import orders_bp
from routes.premium import premium_bp
from routes.products import products_bp


def seed_data():
    if Category.query.count() == 0:
        categories = [
            Category(name='Pasteles', description='Pasteles suaves y esponjosos'),
            Category(name='Galletas', description='Galletas con textura de dulzor casero'),
            Category(name='Brownies', description='Brownies crocantes y húmedos'),
            Category(name='Postres en vaso', description='Postres lista para disfrutar'),
            Category(name='Especiales', description='Menciones exclusivas del día'),
            Category(name='Combos', description='Kits para compartir'),
        ]
        db.session.add_all(categories)
        db.session.commit()

    if Product.query.count() == 0:
        cat_map = {category.name: category for category in Category.query.all()}
        products = [
            Product(name='Pastel de Fresa', description='Esponjoso y con crema de vainilla.', price=25000, image='/static/img/products/pastel-de-fresa.svg', available=True, stock=12, category_id=cat_map['Pasteles'].id),
            Product(name='Brownie de Chocolate', description='Con nuez y un toque muy intenso de cacao.', price=12000, image='/static/img/products/brownie-de-chocolate.svg', available=True, stock=18, category_id=cat_map['Brownies'].id),
            Product(name='Postre en Vaso Oreo', description='Capas de crema y galleta Oreo con textura suave.', price=10000, image='/static/img/products/postre-en-vaso-oreo.svg', available=True, stock=25, category_id=cat_map['Postres en vaso'].id),
            Product(name='Galletas Choco Chip', description='Crujientes por fuera y suaves por dentro.', price=8000, image='/static/img/products/galletas-choco-chip.svg', available=True, stock=30, category_id=cat_map['Galletas'].id),
            Product(name='Cheesecake', description='Suave, cremoso y con mezcla de frutos rojos.', price=15000, image='/static/img/products/cheesecake.svg', available=True, stock=10, category_id=cat_map['Especiales'].id),
            Product(name='Tres Leches', description='Bañado en crema tres leches con frutos.', price=18000, image='/static/img/products/tres-leches.svg', available=True, stock=14, category_id=cat_map['Pasteles'].id),
            Product(name='Cupcakes Decorados', description='Decorados con glaseado y fresas.', price=9000, image='/static/img/products/cupcakes-decorados.svg', available=True, stock=22, category_id=cat_map['Especiales'].id),
            Product(name='Tarta de Limón', description='Agridulce y brillante, ideal para cualquier ocasión.', price=17000, image='/static/img/products/tarta-de-limn.svg', available=True, stock=9, category_id=cat_map['Pasteles'].id),
            Product(name='Combo de Postres', description='Un mix de sabores para compartir.', price=25000, image='/static/img/products/combo-de-postres.svg', available=True, stock=8, category_id=cat_map['Combos'].id),
            Product(name='Pastel de Chocolate', description='Mousse intenso, elegante y muy seductor.', price=22000, image='/static/img/products/pastel-de-chocolate.svg', available=True, stock=11, category_id=cat_map['Pasteles'].id),
        ]
        db.session.add_all(products)
        db.session.commit()

    if Recipe.query.count() == 0:
        recipes = [
            Recipe(name='Galletas caseras', description='Galletas suaves con chips de chocolate.', ingredients='Harina, azúcar, mantequilla, chips de chocolate, huevo, vainilla.', instructions='1. Mezcla mantequilla con azúcar.\n2. Añade huevo y vainilla.\n3. Incorpora la harina y las chispas.\n4. Hornea hasta dorar.', prep_time='35 min', servings=12, image='/static/img/products/galletas-choco-chip.svg'),
            Recipe(name='Brownie intenso', description='Brownie húmedo con un centro muy suave.', ingredients='Cacao, mantequilla, azúcar, huevo, harina, nueces.', instructions='1. Derrite la mantequilla y mezcla con azúcar.\n2. Incorpora huevos y cacao.\n3. Añade harina y nueces.\n4. Hornea a temperatura media.', prep_time='40 min', servings=8, image='/static/img/products/brownie-de-chocolate.svg'),
            Recipe(name='Postre Oreo en vaso', description='Capa a capa con suavidad y sabor intenso.', ingredients='Galletas Oreo, queso crema, leche condensada, vainilla.', instructions='1. Mezcla queso crema con leche condensada.\n2. Agrega vainilla y crema.\n3. Arma capas en vasos.\n4. Refrigera por 2 horas.', prep_time='25 min', servings=4, image='/static/img/products/postre-en-vaso-oreo.svg'),
        ]
        db.session.add_all(recipes)
        db.session.commit()

    if PremiumPlan.query.count() == 0:
        plans = [
            PremiumPlan(name='SweetDreams Plus', description='Acceso premium con beneficios y recetas exclusivas.', price=19000, benefits='Descuentos exclusivos\nRecetas especiales\nPromociones mensuales\nAcceso anticipado', is_active=True),
            PremiumPlan(name='SweetDreams VIP', description='Experiencia completa para los amantes de los dulces.', price=29000, benefits='Todo lo de Plus\nEnvíos gratis\nProductos exclusivos\nDescuentos permanentes', is_active=True),
        ]
        db.session.add_all(plans)
        db.session.commit()

    if Review.query.count() == 0:
        user = User.query.filter_by(email='admin@sweetdreams.com').first()
        if user is None:
            user = User(name='Administrador', email='admin@sweetdreams.com', password='admin123', role='admin')
            db.session.add(user)
            db.session.commit()
        product = Product.query.first()
        if product:
            reviews = [
                Review(user_id=user.id, product_id=product.id, rating=5, comment='Los postres están deliciosos y muy bien presentados.'),
                Review(user_id=user.id, product_id=product.id, rating=4, comment='La entrega fue rápida y el sabor excelente.')
            ]
            db.session.add_all(reviews)
            db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(premium_bp)
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('auth.login'))

    @app.context_processor
    def inject_globals():
        cart = session.get('cart', {})
        count = sum(int(v) for v in cart.values() if isinstance(v, int))
        return {'cart_count': count}

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500

    with app.app_context():
        db.create_all()
        migrate_recipe_difficulty()
        seed_data()
        seed_catalog()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
