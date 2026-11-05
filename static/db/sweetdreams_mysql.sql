-- Esquema MySQL de SweetDreams. Importar dentro de la base de datos creada por el proveedor.

-- El catalogo inicial se carga automaticamente al iniciar la aplicacion Flask.

SET NAMES utf8mb4;

CREATE TABLE categories (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(80) NOT NULL, 
	description TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE TABLE premium_plans (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(80) NOT NULL, 
	description TEXT NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	benefits TEXT NOT NULL, 
	is_active BOOL NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE recipes (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	description TEXT NOT NULL, 
	ingredients TEXT NOT NULL, 
	instructions TEXT NOT NULL, 
	prep_time VARCHAR(50) NOT NULL, 
	servings INTEGER, 
	image VARCHAR(255) NOT NULL, 
	difficulty VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	`role` VARCHAR(20) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);

CREATE TABLE addresses (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	label VARCHAR(80), 
	line1 VARCHAR(255) NOT NULL, 
	city VARCHAR(80) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	is_default BOOL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE orders (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER, 
	delivery_address TEXT NOT NULL, 
	contact_phone VARCHAR(20) NOT NULL, 
	total NUMERIC(10, 2) NOT NULL, 
	status VARCHAR(30) NOT NULL, 
	delivery_method VARCHAR(50) NOT NULL, 
	payment_method VARCHAR(50) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE products (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	description TEXT NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	image VARCHAR(255) NOT NULL, 
	available BOOL NOT NULL, 
	stock INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	FOREIGN KEY(category_id) REFERENCES categories (id)
);

CREATE TABLE subscriptions (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	started_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(plan_id) REFERENCES premium_plans (id)
);

CREATE TABLE cart_items (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE order_items (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	order_id INTEGER NOT NULL, 
	product_id INTEGER, 
	product_name VARCHAR(120) NOT NULL, 
	product_price NUMERIC(10, 2) NOT NULL, 
	quantity INTEGER NOT NULL, 
	subtotal NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE reviews (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	product_id INTEGER, 
	rating INTEGER NOT NULL, 
	comment TEXT NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);
