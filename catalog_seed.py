from html import escape
from pathlib import Path
import re

from flask import current_app
from sqlalchemy import inspect, text

from extensions import db
from models import Category, Product, Recipe


CATEGORY_DESCRIPTIONS = {
    'Pasteles': 'Pasteles artesanales para celebrar y compartir.',
    'Galletas': 'Galletas horneadas en pequeños lotes.',
    'Brownies': 'Brownies húmedos con cacao y chocolate de calidad.',
    'Postres en vaso': 'Postres individuales en capas, listos para disfrutar.',
    'Especiales': 'Creaciones especiales de temporada.',
    'Combos': 'Selecciones dulces pensadas para compartir.',
}

PRODUCTS = [
    ('Pastel de Fresa', 'Bizcocho de vainilla, crema batida y fresas frescas.', 25000, 'Pasteles'),
    ('Brownie de Chocolate', 'Brownie húmedo de chocolate oscuro con nuez tostada.', 12000, 'Brownies'),
    ('Postre en Vaso Oreo', 'Capas de crema de vainilla y galleta de cacao.', 10000, 'Postres en vaso'),
    ('Galletas Choco Chip', 'Galletas doradas, suaves al centro y con chocolate.', 8000, 'Galletas'),
    ('Cheesecake', 'Tarta cremosa con base crocante y frutos rojos.', 15000, 'Especiales'),
    ('Tres Leches', 'Bizcocho ligero bañado en tres leches y crema.', 18000, 'Pasteles'),
    ('Cupcakes Decorados', 'Cupcakes de vainilla con crema y decoración artesanal.', 9000, 'Especiales'),
    ('Tarta de Limón', 'Tarta de limón fresco con merengue tostado.', 17000, 'Pasteles'),
    ('Combo de Postres', 'Selección de porciones de nuestros postres favoritos.', 25000, 'Combos'),
    ('Pastel de Chocolate', 'Bizcocho de cacao con ganache de chocolate semiamargo.', 22000, 'Pasteles'),
    ('Torta Red Velvet', 'Bizcocho red velvet con frosting suave de queso crema.', 28000, 'Pasteles'),
    ('Torta de Zanahoria', 'Bizcocho especiado de zanahoria con nueces y frosting.', 24000, 'Pasteles'),
    ('Torta de Vainilla y Arequipe', 'Capas de vainilla rellenas de arequipe artesanal.', 26000, 'Pasteles'),
    ('Torta de Naranja', 'Bizcocho húmedo de naranja con glaseado cítrico.', 21000, 'Pasteles'),
    ('Torta de Coco', 'Bizcocho de coco con crema ligera y coco tostado.', 23000, 'Pasteles'),
    ('Torta de Maracuyá', 'Torta suave con mousse de maracuyá y base de vainilla.', 27000, 'Pasteles'),
    ('Torta Selva Negra', 'Chocolate, crema y cerezas en una combinación clásica.', 30000, 'Pasteles'),
    ('Torta de Banano', 'Panqué de banano maduro con canela y nueces.', 19000, 'Pasteles'),
    ('Cheesecake de Maracuyá', 'Cheesecake horneado con cobertura de maracuyá.', 19000, 'Especiales'),
    ('Cheesecake de Oreo', 'Relleno cremoso con galleta de cacao y base crocante.', 20000, 'Especiales'),
    ('Cheesecake de Limón', 'Cheesecake fresco con ralladura y jugo de limón.', 18500, 'Especiales'),
    ('Cheesecake de Arequipe', 'Cheesecake cremoso con vetas de arequipe.', 21000, 'Especiales'),
    ('Brownie con Arequipe', 'Brownie de cacao terminado con arequipe colombiano.', 14000, 'Brownies'),
    ('Brownie de Nuez', 'Chocolate intenso y nueces tostadas en cada porción.', 13500, 'Brownies'),
    ('Brownie de Café', 'Brownie de chocolate con notas aromáticas de café.', 13000, 'Brownies'),
    ('Blondie de Chocolate Blanco', 'Cuadrado de vainilla y chocolate blanco dorado.', 12500, 'Brownies'),
    ('Galletas de Avena y Pasas', 'Galletas de avena con pasas y un toque de canela.', 7500, 'Galletas'),
    ('Galletas de Limón', 'Galletas mantequillosas con glaseado de limón.', 8000, 'Galletas'),
    ('Galletas de Red Velvet', 'Galletas suaves de cacao con trozos de chocolate blanco.', 9500, 'Galletas'),
    ('Galletas de Mantequilla', 'Galletas clásicas de mantequilla, delicadas y crujientes.', 7000, 'Galletas'),
    ('Alfajores de Arequipe', 'Dos tapas suaves unidas por arequipe y coco.', 9000, 'Galletas'),
    ('Cupcake de Chocolate', 'Cupcake de cacao con crema de chocolate.', 9500, 'Especiales'),
    ('Cupcake de Red Velvet', 'Cupcake red velvet con frosting de queso crema.', 10000, 'Especiales'),
    ('Cupcake de Limón', 'Cupcake cítrico con crema ligera de limón.', 9000, 'Especiales'),
    ('Cupcake de Zanahoria', 'Cupcake especiado de zanahoria con frosting.', 9500, 'Especiales'),
    ('Vasito de Tiramisú', 'Capas de bizcocho al café y crema de mascarpone.', 12000, 'Postres en vaso'),
    ('Vasito de Tres Leches', 'Bizcocho bañado y crema suave en presentación individual.', 11000, 'Postres en vaso'),
    ('Vasito de Cheesecake de Fresa', 'Crema de cheesecake, galleta y salsa de fresa.', 11500, 'Postres en vaso'),
    ('Vasito de Mousse de Chocolate', 'Mousse aireado de chocolate con virutas.', 10500, 'Postres en vaso'),
    ('Vasito de Maracuyá', 'Crema de maracuyá con crumble de vainilla.', 10500, 'Postres en vaso'),
    ('Vasito de Pie de Limón', 'Crema de limón, galleta y merengue tostado.', 11000, 'Postres en vaso'),
    ('Macarons Surtidos', 'Caja de seis macarons de sabores surtidos.', 18000, 'Especiales'),
    ('Éclair de Vainilla', 'Pasta choux rellena de crema pastelera de vainilla.', 10500, 'Especiales'),
    ('Profiteroles de Chocolate', 'Bocaditos de pasta choux con crema y salsa de chocolate.', 16000, 'Especiales'),
    ('Tartaleta de Frutos Rojos', 'Tartaleta de crema pastelera con frutos rojos frescos.', 16000, 'Especiales'),
    ('Combo de Galletas', 'Caja de ocho galletas artesanales surtidas.', 28000, 'Combos'),
    ('Combo Brownie y Café', 'Dos brownies de la casa con café molido para preparar.', 24000, 'Combos'),
    ('Caja Celebración', 'Selección para compartir de cupcakes, brownies y galletas.', 42000, 'Combos'),
    ('Mini Postres Surtidos', 'Doce mini bocados dulces para reuniones y celebraciones.', 36000, 'Combos'),
    ('Caja de Cupcakes', 'Seis cupcakes decorados en sabores surtidos.', 52000, 'Combos'),
]

RECIPES = [
    (
        'Galletas caseras', 'Galletas suaves por dentro y doradas en los bordes.',
        'Harina de trigo: 250 g\nMantequilla sin sal blanda: 125 g\nAzúcar morena: 100 g\nAzúcar blanca: 60 g\nHuevo: 1 (50 g)\nVainilla: 5 ml\nBicarbonato: 3 g\nSal: 2 g\nChips de chocolate: 150 g',
        '1. Precalienta el horno a 180 °C y cubre una bandeja con papel para hornear.\n2. Bate la mantequilla con ambos azúcares durante 2 minutos.\n3. Agrega el huevo y la vainilla; mezcla hasta integrar.\n4. Incorpora harina, bicarbonato y sal sin sobrebatir; añade los chips.\n5. Forma 12 porciones, sepáralas 5 cm y hornea de 10 a 12 minutos.\n6. Deja reposar 10 minutos en la bandeja antes de servir.',
        '35 min', 12, 'Fácil', 'cookie',
    ),
    (
        'Brownie intenso', 'Brownie húmedo de chocolate con superficie ligeramente crocante.',
        'Chocolate semiamargo: 200 g\nMantequilla: 150 g\nAzúcar: 180 g\nHuevos: 3\nHarina: 90 g\nCacao sin azúcar: 25 g\nSal: 2 g\nNueces picadas: 80 g',
        '1. Precalienta el horno a 175 °C y forra un molde cuadrado de 20 cm.\n2. Derrite el chocolate con la mantequilla a baño María y deja entibiar.\n3. Bate los huevos con el azúcar hasta que estén brillantes; incorpora el chocolate.\n4. Tamiza harina, cacao y sal; mezcla apenas hasta integrar y añade las nueces.\n5. Vierte en el molde y hornea de 22 a 27 minutos; el centro debe quedar húmedo.\n6. Enfría por completo antes de cortar en 8 porciones.',
        '45 min', 8, 'Fácil', 'brownie',
    ),
    (
        'Postre Oreo en vaso', 'Postre frío en capas de galleta y crema de queso.',
        'Galletas de cacao tipo sándwich: 180 g\nQueso crema: 250 g\nCrema para batir fría: 200 ml\nLeche condensada: 120 g\nVainilla: 5 ml\nMantequilla derretida: 30 g',
        '1. Separa 6 galletas para decorar y tritura el resto; mezcla con la mantequilla.\n2. Bate el queso crema con la leche condensada y la vainilla hasta que quede liso.\n3. Bate la crema fría a picos suaves e incorpórala con movimientos envolventes.\n4. Reparte la galleta triturada y la crema en capas dentro de 4 vasos.\n5. Refrigera al menos 3 horas y decora con las galletas reservadas.',
        '25 min + 3 h de frío', 4, 'Fácil', 'jar',
    ),
    (
        'Torta de vainilla esponjosa', 'Bizcocho tierno con miga aireada y aroma de vainilla.',
        'Harina: 240 g\nAzúcar: 200 g\nMantequilla blanda: 150 g\nHuevos: 3\nLeche: 180 ml\nPolvo de hornear: 8 g\nVainilla: 10 ml\nSal: 2 g',
        '1. Calienta el horno a 175 °C y engrasa un molde redondo de 22 cm.\n2. Bate mantequilla y azúcar durante 4 minutos hasta obtener una crema pálida.\n3. Añade los huevos de uno en uno y luego la vainilla.\n4. Combina harina, polvo de hornear y sal; agrégalos alternando con la leche.\n5. Vierte la mezcla y hornea de 30 a 35 minutos, hasta que el palillo salga limpio.\n6. Deja enfriar 15 minutos, desmolda y enfría por completo.',
        '55 min', 10, 'Media', 'cake',
    ),
    (
        'Cheesecake de frutos rojos', 'Tarta cremosa con base de galleta y salsa de frutos rojos.',
        'Galletas de vainilla: 200 g\nMantequilla: 85 g\nQueso crema: 500 g\nAzúcar: 150 g\nHuevos: 2\nCrema agria: 120 g\nVainilla: 5 ml\nFrutos rojos: 200 g\nAzúcar para salsa: 40 g',
        '1. Precalienta el horno a 160 °C. Tritura las galletas y mézclalas con mantequilla.\n2. Presiona la mezcla en un molde desmontable de 20 cm y hornea 8 minutos.\n3. Bate queso crema y azúcar a velocidad baja; añade huevos uno a uno, crema agria y vainilla.\n4. Vierte el relleno sobre la base y hornea 50 minutos; el centro debe temblar ligeramente.\n5. Apaga el horno, deja la puerta entreabierta 30 minutos y luego enfría 4 horas.\n6. Cocina los frutos rojos con 40 g de azúcar 8 minutos; enfría y sirve encima.',
        '1 h 20 min + 4 h de frío', 10, 'Media', 'cake',
    ),
    (
        'Torta de zanahoria', 'Bizcocho húmedo con especias, nueces y cobertura de queso.',
        'Zanahoria rallada: 250 g\nHarina: 220 g\nAzúcar morena: 180 g\nAceite vegetal: 150 ml\nHuevos: 3\nNueces: 80 g\nCanela: 5 g\nPolvo de hornear: 8 g\nQueso crema: 200 g\nAzúcar pulverizada: 100 g',
        '1. Precalienta el horno a 175 °C y engrasa un molde de 22 cm.\n2. Bate huevos, azúcar y aceite hasta integrar.\n3. Mezcla harina, canela y polvo de hornear; incorpóralos a los líquidos.\n4. Añade zanahoria y nueces; vierte en el molde.\n5. Hornea de 40 a 45 minutos y enfría completamente.\n6. Bate queso crema con azúcar pulverizada y cubre la torta fría.',
        '1 h 10 min', 10, 'Media', 'cake',
    ),
    (
        'Tarta de limón y merengue', 'Relleno cítrico sedoso sobre masa quebrada y merengue tostado.',
        'Harina: 220 g\nMantequilla fría: 110 g\nAzúcar pulverizada: 40 g\nYema: 1\nLeche condensada: 300 g\nYemas para relleno: 3\nJugo de limón: 120 ml\nClaras: 3\nAzúcar para merengue: 150 g',
        '1. Arenar harina, mantequilla y azúcar; añadir yema y 15 ml de agua fría. Reposar 30 minutos.\n2. Estirar, forrar un molde de 22 cm y hornear con peso 15 minutos a 180 °C; retirar el peso y hornear 8 minutos más.\n3. Mezclar leche condensada, yemas y jugo de limón; verter sobre la base y hornear 12 minutos.\n4. Calentar claras y azúcar a baño María hasta disolver el azúcar; batir hasta lograr merengue firme.\n5. Cubrir la tarta fría con merengue y dorar con soplete o bajo el grill.',
        '1 h 30 min', 8, 'Media', 'tart',
    ),
    (
        'Cupcakes de chocolate', 'Cupcakes de cacao con crema ligera de chocolate.',
        'Harina: 180 g\nAzúcar: 180 g\nCacao: 35 g\nPolvo de hornear: 6 g\nLeche: 180 ml\nAceite: 80 ml\nHuevo: 1\nVainilla: 5 ml\nChocolate: 150 g\nCrema para batir: 120 ml',
        '1. Precalienta el horno a 175 °C y coloca 12 capacillos en un molde.\n2. Mezcla harina, azúcar, cacao y polvo de hornear.\n3. Añade leche, aceite, huevo y vainilla; bate solo hasta integrar.\n4. Llena cada capacillo hasta dos tercios y hornea 18 a 20 minutos.\n5. Calienta la crema, viértela sobre el chocolate picado y mezcla; enfría hasta que espese.\n6. Decora los cupcakes completamente fríos.',
        '45 min', 12, 'Fácil', 'cupcake',
    ),
    (
        'Torta tres leches', 'Bizcocho aireado empapado con mezcla de tres leches.',
        'Huevos: 5\nAzúcar: 150 g\nHarina: 150 g\nPolvo de hornear: 5 g\nLeche evaporada: 250 ml\nLeche condensada: 250 ml\nCrema de leche: 200 ml\nVainilla: 5 ml\nCrema para cubrir: 250 ml',
        '1. Precalienta el horno a 175 °C y engrasa un molde de 23 x 33 cm.\n2. Separa los huevos; bate claras a punto de nieve y agrega el azúcar poco a poco.\n3. Incorpora yemas, luego harina y polvo tamizados con movimientos envolventes.\n4. Hornea de 25 a 30 minutos y pincha toda la superficie con un tenedor.\n5. Mezcla las tres leches con vainilla, vierte lentamente sobre el bizcocho y refrigera 4 horas.\n6. Bate la crema y cubre antes de servir.',
        '55 min + 4 h de frío', 12, 'Media', 'cake',
    ),
    (
        'Galletas de avena y pasas', 'Galletas rústicas con avena, canela y pasas jugosas.',
        'Avena en hojuelas: 180 g\nHarina: 120 g\nMantequilla: 110 g\nAzúcar morena: 130 g\nHuevo: 1\nPasas: 100 g\nCanela: 3 g\nBicarbonato: 3 g\nSal: 2 g',
        '1. Calienta el horno a 180 °C y prepara dos bandejas.\n2. Bate mantequilla con azúcar; añade el huevo.\n3. Mezcla harina, avena, canela, bicarbonato y sal; incorpora a la preparación.\n4. Agrega las pasas y deja reposar la masa 10 minutos.\n5. Forma 16 bolitas, aplánalas ligeramente y hornea de 12 a 14 minutos.\n6. Enfría en rejilla para que queden firmes.',
        '35 min', 16, 'Fácil', 'cookie',
    ),
    (
        'Mousse de chocolate', 'Mousse aireado de chocolate oscuro con textura sedosa.',
        'Chocolate semiamargo: 200 g\nHuevos: 3, separados\nAzúcar: 35 g\nCrema para batir: 200 ml\nSal: 1 pizca\nVainilla: 5 ml',
        '1. Derrite el chocolate a baño María y deja que se entibie.\n2. Bate las yemas con la vainilla y mezcla con el chocolate.\n3. Bate la crema a picos suaves e incorpórala en dos tandas.\n4. Bate las claras con sal; agrega el azúcar y continúa hasta obtener picos firmes.\n5. Integra las claras con movimientos envolventes para no perder aire.\n6. Reparte en 6 copas y refrigera al menos 3 horas.',
        '30 min + 3 h de frío', 6, 'Media', 'jar',
    ),
    (
        'Tarta de manzana', 'Tarta de manzana con canela y masa dorada.',
        'Harina: 250 g\nMantequilla fría: 140 g\nAzúcar: 90 g\nAgua fría: 45 ml\nManzanas: 700 g\nCanela: 4 g\nMaicena: 15 g\nJugo de limón: 15 ml\nHuevo para pincelar: 1',
        '1. Mezcla harina con 30 g de azúcar y mantequilla hasta obtener migas; añade agua y une sin amasar.\n2. Refrigera la masa 30 minutos. Pela y corta las manzanas en láminas.\n3. Mezcla manzana con azúcar restante, canela, maicena y limón.\n4. Estira dos tercios de la masa y cubre un molde de 23 cm; rellena con manzana.\n5. Cubre con tiras de masa, sella y pincela con huevo.\n6. Hornea a 190 °C durante 45 a 50 minutos; reposa antes de cortar.',
        '1 h 30 min', 8, 'Media', 'tart',
    ),
    (
        'Flan de caramelo', 'Flan de vainilla suave con caramelo hecho en casa.',
        'Azúcar para caramelo: 120 g\nLeche: 500 ml\nLeche condensada: 200 g\nHuevos: 4\nYemas: 2\nVainilla: 5 ml\nSal: 1 pizca',
        '1. Precalienta el horno a 160 °C y prepara una fuente para baño María.\n2. Derrite el azúcar en una olla sin revolver hasta obtener caramelo ámbar; viértelo en el molde.\n3. Calienta la leche sin hervir y mezcla con leche condensada.\n4. Bate suavemente huevos, yemas, vainilla y sal; incorpora la leche tibia en hilo.\n5. Cuela, vierte en el molde y hornea a baño María de 55 a 65 minutos.\n6. Enfría, refrigera 4 horas y desmolda pasando un cuchillo por el borde.',
        '1 h 20 min + 4 h de frío', 8, 'Media', 'jar',
    ),
    (
        'Tiramisú clásico', 'Capas de bizcochos al café con crema de mascarpone.',
        'Queso mascarpone: 400 g\nHuevos: 4, separados\nAzúcar: 100 g\nBizcochos de soletilla: 24\nCafé fuerte frío: 300 ml\nCacao sin azúcar: 20 g\nSal: 1 pizca',
        '1. Prepara el café y déjalo enfriar por completo.\n2. Bate las yemas con azúcar hasta que estén pálidas; incorpora el mascarpone.\n3. Bate las claras con una pizca de sal a punto firme e intégralas con cuidado.\n4. Pasa cada bizcocho rápidamente por el café y forma una capa en una fuente.\n5. Cubre con la mitad de la crema y repite las capas.\n6. Refrigera al menos 6 horas; espolvorea cacao justo antes de servir.',
        '35 min + 6 h de frío', 8, 'Media', 'jar',
    ),
    (
        'Cheesecake de limón sin horno', 'Cheesecake fresco con relleno de limón y base crujiente.',
        'Galletas tipo digestive: 220 g\nMantequilla: 90 g\nQueso crema: 400 g\nCrema para batir: 250 ml\nAzúcar pulverizada: 100 g\nJugo de limón: 70 ml\nRalladura de limón: 1\nGelatina sin sabor: 7 g\nAgua: 35 ml',
        '1. Tritura las galletas y mezcla con mantequilla; presiona en un molde de 20 cm y refrigera.\n2. Hidrata la gelatina en agua 10 minutos y disuélvela suavemente.\n3. Bate queso crema con azúcar, jugo y ralladura de limón.\n4. Bate la crema a picos suaves e incorpórala al queso junto con la gelatina tibia.\n5. Vierte sobre la base y alisa la superficie.\n6. Refrigera al menos 6 horas antes de desmoldar.',
        '30 min + 6 h de frío', 10, 'Fácil', 'cake',
    ),
    (
        'Alfajores de arequipe', 'Tapas delicadas de maicena rellenas de arequipe.',
        'Maicena: 200 g\nHarina: 100 g\nMantequilla blanda: 120 g\nAzúcar: 80 g\nYemas: 2\nPolvo de hornear: 5 g\nVainilla: 5 ml\nArequipe: 250 g\nCoco rallado: 50 g',
        '1. Precalienta el horno a 170 °C y cubre una bandeja con papel.\n2. Bate mantequilla y azúcar; agrega yemas y vainilla.\n3. Tamiza maicena, harina y polvo de hornear; mezcla hasta formar una masa suave.\n4. Refrigera 20 minutos, estira a 5 mm y corta 24 discos pequeños.\n5. Hornea de 8 a 10 minutos sin dejar que se doren demasiado; enfría.\n6. Une de a dos con arequipe y pasa los bordes por coco.',
        '55 min', 12, 'Media', 'cookie',
    ),
    (
        'Cupcakes de zanahoria', 'Porciones especiadas y húmedas con crema de queso.',
        'Zanahoria rallada: 180 g\nHarina: 190 g\nAzúcar morena: 150 g\nAceite: 120 ml\nHuevos: 2\nCanela: 4 g\nPolvo de hornear: 6 g\nNueces: 50 g\nQueso crema: 180 g\nAzúcar pulverizada: 80 g',
        '1. Precalienta el horno a 175 °C y prepara 12 capacillos.\n2. Bate huevos, azúcar y aceite; incorpora zanahoria.\n3. Añade harina, canela y polvo de hornear tamizados; integra las nueces.\n4. Reparte la mezcla y hornea de 18 a 21 minutos; enfría completamente.\n5. Bate queso crema y azúcar pulverizada hasta obtener una crema lisa.\n6. Decora cada cupcake frío con la cobertura.',
        '45 min', 12, 'Fácil', 'cupcake',
    ),
    (
        'Tarta de chocolate', 'Tarta de ganache intensa en una base de cacao crujiente.',
        'Galletas de chocolate: 220 g\nMantequilla: 90 g\nChocolate semiamargo: 300 g\nCrema de leche: 250 ml\nMiel: 20 g\nSal: 1 pizca\nFrutos rojos: 100 g',
        '1. Tritura las galletas, mézclalas con mantequilla y presiona en un molde de 22 cm.\n2. Hornea la base 10 minutos a 175 °C y deja enfriar.\n3. Calienta la crema con miel hasta que aparezcan burbujas en el borde.\n4. Vierte sobre el chocolate picado, espera 2 minutos y mezcla hasta lograr una ganache brillante.\n5. Añade sal, vierte sobre la base y refrigera 3 horas.\n6. Decora con frutos rojos antes de servir.',
        '35 min + 3 h de frío', 10, 'Fácil', 'tart',
    ),
    (
        'Panna cotta de vainilla', 'Postre italiano delicado con salsa de frutos rojos.',
        'Crema de leche: 400 ml\nLeche: 100 ml\nAzúcar: 70 g\nGelatina sin sabor: 7 g\nAgua: 35 ml\nVainilla: 10 ml\nFresas: 150 g\nAzúcar para salsa: 25 g',
        '1. Hidrata la gelatina en agua fría durante 10 minutos.\n2. Calienta crema, leche, azúcar y vainilla sin dejar que hiervan.\n3. Retira del fuego y disuelve la gelatina hidratada en la mezcla caliente.\n4. Reparte en 6 moldes ligeramente engrasados y refrigera 4 horas.\n5. Cocina las fresas con 25 g de azúcar durante 5 minutos y deja enfriar.\n6. Desmolda y sirve con la salsa.',
        '25 min + 4 h de frío', 6, 'Fácil', 'jar',
    ),
    (
        'Galletas de mantequilla', 'Galletas clásicas, delicadas y perfectas para acompañar café.',
        'Harina: 250 g\nMantequilla blanda: 170 g\nAzúcar pulverizada: 80 g\nYema: 1\nVainilla: 5 ml\nSal: 2 g',
        '1. Precalienta el horno a 170 °C y prepara una bandeja.\n2. Bate mantequilla y azúcar pulverizada hasta que la mezcla esté cremosa.\n3. Agrega yema, vainilla y sal.\n4. Incorpora la harina hasta obtener una masa uniforme; refrigera 20 minutos.\n5. Estira a 6 mm, corta figuras y acomódalas en la bandeja.\n6. Hornea de 10 a 12 minutos, hasta que apenas doren los bordes.',
        '45 min', 20, 'Fácil', 'cookie',
    ),
    (
        'Panqué de banano', 'Panqué húmedo de banano maduro con nueces.',
        'Banano muy maduro: 3 (300 g sin cáscara)\nHarina: 220 g\nAzúcar morena: 120 g\nMantequilla derretida: 90 g\nHuevos: 2\nPolvo de hornear: 6 g\nCanela: 3 g\nNueces: 70 g\nSal: 2 g',
        '1. Precalienta el horno a 175 °C y engrasa un molde rectangular.\n2. Tritura los bananos y mézclalos con mantequilla, huevos y azúcar.\n3. Combina harina, polvo de hornear, canela y sal; integra a los líquidos.\n4. Añade las nueces sin sobremezclar.\n5. Vierte en el molde y hornea de 50 a 55 minutos.\n6. Enfría 15 minutos en el molde y luego sobre rejilla.',
        '1 h 15 min', 10, 'Fácil', 'cake',
    ),
    (
        'Macarons de vainilla', 'Macarons delicados con relleno de ganache blanca.',
        'Harina de almendra: 100 g\nAzúcar pulverizada: 100 g\nClaras: 75 g\nAzúcar blanca: 75 g\nColorante en gel: unas gotas\nChocolate blanco: 120 g\nCrema de leche: 50 ml',
        '1. Tamiza dos veces harina de almendra y azúcar pulverizada.\n2. Bate claras; cuando espumen, añade azúcar blanca poco a poco hasta obtener picos firmes.\n3. Incorpora los secos y mezcla hasta que la masa caiga en cinta continua; añade colorante.\n4. Forma círculos de 3 cm sobre tapete, golpea la bandeja y deja secar 30 a 45 minutos.\n5. Hornea a 150 °C durante 14 a 16 minutos y deja enfriar.\n6. Rellena con ganache hecha al mezclar crema caliente y chocolate; madura 12 horas en frío.',
        '1 h 30 min + 12 h de reposo', 20, 'Difícil', 'cookie',
    ),
    (
        'Éclairs de crema pastelera', 'Pasta choux ligera rellena de crema de vainilla.',
        'Agua: 125 ml\nLeche: 125 ml\nMantequilla: 100 g\nHarina: 150 g\nHuevos: 4\nLeche para crema: 400 ml\nYemas para crema: 4\nAzúcar para crema: 90 g\nMaicena: 35 g\nVainilla: 10 ml',
        '1. Calienta leche, agua, mantequilla y sal hasta hervir; añade harina de una vez y mezcla hasta formar una bola.\n2. Cocina la masa 2 minutos; enfría 5 minutos e incorpora los huevos uno a uno.\n3. Forma 12 tiras con manga y hornea a 200 °C 15 minutos; baja a 180 °C y hornea 20 minutos más.\n4. Para la crema, calienta la leche con vainilla. Bate yemas, azúcar y maicena.\n5. Vierte leche caliente sobre las yemas, devuelve a la olla y cocina hasta espesar; enfría cubierta.\n6. Rellena los éclairs fríos con crema.',
        '1 h 30 min', 12, 'Difícil', 'tart',
    ),
    (
        'Crumble de manzana', 'Manzanas especiadas bajo una cubierta crujiente de avena.',
        'Manzanas: 700 g\nJugo de limón: 15 ml\nAzúcar morena: 80 g\nCanela: 4 g\nHarina: 100 g\nAvena: 80 g\nMantequilla fría: 90 g\nSal: 1 pizca',
        '1. Precalienta el horno a 180 °C y engrasa una fuente mediana.\n2. Pela y corta las manzanas; mézclalas con limón, 30 g de azúcar y la canela.\n3. Combina harina, avena, azúcar restante y sal.\n4. Añade mantequilla fría en cubos y frota con los dedos hasta formar migas.\n5. Reparte la cubierta sobre las manzanas y hornea 35 a 40 minutos.\n6. Reposa 15 minutos y sirve tibio.',
        '1 h', 8, 'Fácil', 'tart',
    ),
    (
        'Trufas de chocolate', 'Bocados de ganache cubiertos de cacao y frutos secos.',
        'Chocolate semiamargo: 250 g\nCrema de leche: 150 ml\nMantequilla: 25 g\nCacao sin azúcar: 40 g\nNueces picadas: 50 g\nVainilla: 5 ml',
        '1. Pica finamente el chocolate y colócalo en un recipiente resistente al calor.\n2. Calienta la crema hasta que humee; viértela sobre el chocolate y espera 2 minutos.\n3. Mezcla desde el centro hasta emulsionar; agrega mantequilla y vainilla.\n4. Refrigera la ganache 2 horas hasta que se pueda moldear.\n5. Forma 20 bolitas con las manos frías.\n6. Pásalas por cacao o nueces y conserva refrigeradas.',
        '25 min + 2 h de frío', 20, 'Fácil', 'brownie',
    ),
    (
        'Torta red velvet', 'Bizcocho rojo aterciopelado con frosting de queso crema.',
        'Harina: 280 g\nAzúcar: 250 g\nAceite: 180 ml\nHuevos: 2\nSuero de leche: 240 ml\nCacao: 15 g\nVinagre: 5 ml\nColorante rojo: 10 ml\nBicarbonato: 5 g\nQueso crema: 300 g\nMantequilla: 100 g\nAzúcar pulverizada: 180 g',
        '1. Calienta el horno a 175 °C y engrasa dos moldes de 20 cm.\n2. Bate aceite, azúcar y huevos; mezcla aparte suero de leche, vinagre y colorante.\n3. Tamiza harina, cacao y bicarbonato; alterna los secos y el suero en la mezcla de huevos.\n4. Divide en moldes y hornea de 25 a 30 minutos; enfría.\n5. Bate queso crema, mantequilla y azúcar pulverizada hasta que el frosting quede suave.\n6. Rellena y cubre las capas ya frías.',
        '1 h 20 min', 12, 'Media', 'cake',
    ),
    (
        'Tartaletas de frutos rojos', 'Tartaletas crujientes con crema pastelera y fruta fresca.',
        'Harina: 220 g\nMantequilla fría: 110 g\nAzúcar: 60 g\nYema: 1\nLeche: 300 ml\nYemas para crema: 3\nAzúcar para crema: 60 g\nMaicena: 25 g\nVainilla: 5 ml\nFrutos rojos: 250 g',
        '1. Mezcla harina, mantequilla y azúcar hasta obtener migas; une con la yema y refrigera 30 minutos.\n2. Forra 6 moldes pequeños, pincha las bases y hornea a 180 °C durante 15 a 18 minutos.\n3. Calienta la leche con vainilla. Bate yemas, azúcar y maicena.\n4. Templa las yemas con leche caliente y cocina mezclando hasta espesar; enfría cubierta.\n5. Rellena las bases frías con crema pastelera.\n6. Decora con frutos rojos lavados y secos.',
        '1 h 15 min', 6, 'Media', 'tart',
    ),
    (
        'Galletas de limón', 'Galletas tiernas con ralladura y glaseado cítrico.',
        'Harina: 250 g\nMantequilla blanda: 120 g\nAzúcar: 150 g\nHuevo: 1\nRalladura de limón: 2\nJugo de limón: 30 ml\nPolvo de hornear: 5 g\nAzúcar pulverizada: 100 g',
        '1. Precalienta el horno a 175 °C y forra una bandeja.\n2. Bate mantequilla con azúcar y ralladura de limón.\n3. Añade huevo y 15 ml de jugo; incorpora harina y polvo de hornear.\n4. Forma 18 bolitas y aplánalas ligeramente.\n5. Hornea de 10 a 12 minutos y deja enfriar.\n6. Mezcla azúcar pulverizada con el jugo restante y glasea las galletas.',
        '40 min', 18, 'Fácil', 'cookie',
    ),
    (
        'Vasitos de maracuyá', 'Crema fría de maracuyá sobre una base de galleta.',
        'Galletas de vainilla: 150 g\nMantequilla: 50 g\nQueso crema: 250 g\nLeche condensada: 180 g\nPulpa de maracuyá: 120 ml\nCrema para batir: 180 ml\nGelatina sin sabor: 5 g\nAgua: 25 ml',
        '1. Tritura las galletas y mezcla con mantequilla; reparte en 6 vasos y presiona.\n2. Hidrata la gelatina en agua fría durante 10 minutos y disuélvela.\n3. Bate queso crema con leche condensada y pulpa de maracuyá.\n4. Bate la crema a picos suaves e incorpórala junto con la gelatina tibia.\n5. Reparte la mezcla en los vasos.\n6. Refrigera 4 horas y decora con unas gotas de pulpa.',
        '25 min + 4 h de frío', 6, 'Fácil', 'jar',
    ),
    (
        'Profiteroles con chocolate', 'Bocaditos de pasta choux rellenos y bañados en chocolate.',
        'Agua: 125 ml\nMantequilla: 60 g\nHarina: 75 g\nHuevos: 2\nCrema para batir: 250 ml\nAzúcar pulverizada: 25 g\nChocolate semiamargo: 100 g\nCrema de leche para salsa: 80 ml',
        '1. Precalienta el horno a 200 °C y prepara una bandeja con papel.\n2. Hierve agua y mantequilla; añade harina de una vez y mezcla hasta que la masa se despegue.\n3. Enfría 5 minutos e incorpora los huevos uno a uno.\n4. Forma 20 montoncitos y hornea 20 minutos; perfora y deja secar 5 minutos más.\n5. Bate la crema con azúcar pulverizada y rellena los profiteroles fríos.\n6. Calienta crema, viértela sobre el chocolate, mezcla y sirve sobre los profiteroles.',
        '1 h', 10, 'Media', 'cupcake',
    ),
    (
        'Torta de coco', 'Bizcocho húmedo de coco con cobertura cremosa.',
        'Harina: 240 g\nAzúcar: 180 g\nMantequilla: 130 g\nHuevos: 3\nLeche de coco: 180 ml\nCoco rallado: 80 g\nPolvo de hornear: 8 g\nQueso crema: 180 g\nAzúcar pulverizada: 80 g',
        '1. Calienta el horno a 175 °C y engrasa un molde redondo de 22 cm.\n2. Bate mantequilla y azúcar hasta que estén cremosas; añade los huevos uno a uno.\n3. Mezcla harina con polvo de hornear e incorpórala alternando con la leche de coco.\n4. Agrega el coco rallado y vierte en el molde.\n5. Hornea de 35 a 40 minutos y deja enfriar.\n6. Bate queso crema con azúcar pulverizada y cubre la torta fría.',
        '1 h', 10, 'Fácil', 'cake',
    ),
    (
        'Brownie de café', 'Brownie de chocolate con café y nueces tostadas.',
        'Chocolate semiamargo: 180 g\nMantequilla: 140 g\nAzúcar: 170 g\nHuevos: 3\nCafé espresso: 30 ml\nHarina: 95 g\nCacao: 20 g\nNueces: 60 g\nSal: 2 g',
        '1. Precalienta el horno a 175 °C y forra un molde de 20 cm.\n2. Derrite chocolate y mantequilla; mezcla con el espresso y deja entibiar.\n3. Bate huevos y azúcar; incorpora la mezcla de chocolate.\n4. Añade harina, cacao y sal tamizados; integra las nueces.\n5. Hornea de 22 a 26 minutos, dejando el centro ligeramente húmedo.\n6. Enfría por completo antes de cortar.',
        '40 min', 9, 'Fácil', 'brownie',
    ),
    (
        'Torta de maracuyá', 'Bizcocho ligero relleno de crema y curd de maracuyá.',
        'Harina: 250 g\nAzúcar: 200 g\nMantequilla: 140 g\nHuevos: 3\nLeche: 150 ml\nPolvo de hornear: 8 g\nPulpa de maracuyá: 150 ml\nYemas: 3\nAzúcar para curd: 100 g\nMantequilla para curd: 60 g',
        '1. Precalienta el horno a 175 °C; engrasa dos moldes de 18 cm.\n2. Bate mantequilla y azúcar; incorpora huevos uno por uno.\n3. Añade harina y polvo de hornear alternando con leche; divide y hornea 25 minutos.\n4. Cocina pulpa, yemas y azúcar a fuego bajo, mezclando hasta espesar; retira e incorpora mantequilla.\n5. Enfría el curd y los bizcochos por completo.\n6. Rellena las capas con curd y refrigera 1 hora antes de cortar.',
        '1 h 20 min', 10, 'Media', 'cake',
    ),
    (
        'Pudín de pan', 'Postre casero de pan, leche, canela y caramelo.',
        'Pan del día anterior: 350 g\nLeche: 500 ml\nHuevos: 3\nAzúcar: 130 g\nPasas: 60 g\nCanela: 3 g\nVainilla: 5 ml\nAzúcar para caramelo: 100 g',
        '1. Precalienta el horno a 170 °C y prepara una fuente para baño María.\n2. Derrite 100 g de azúcar hasta caramelo y cubre el fondo del molde.\n3. Corta el pan y remójalo en la leche durante 15 minutos.\n4. Bate huevos con el azúcar restante, canela y vainilla; mezcla con el pan y las pasas.\n5. Vierte en el molde y hornea a baño María durante 55 a 65 minutos.\n6. Enfría, refrigera 3 horas y desmolda.',
        '1 h 30 min + 3 h de frío', 8, 'Fácil', 'cake',
    ),
]


def _slug(value):
    value = value.lower().encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-')


def _dessert_svg(name, category, index):
    palettes = {
        'Pasteles': ('#f2b5c5', '#9d4b5c', '#fff0d9'),
        'Galletas': ('#d9a15f', '#7b472d', '#fff2d6'),
        'Brownies': ('#86503d', '#42251f', '#e8b26a'),
        'Postres en vaso': ('#f1c2cf', '#8f5466', '#e7b866'),
        'Especiales': ('#d7a6bb', '#67404c', '#efc77a'),
        'Combos': ('#e4ad85', '#7d4942', '#f3d37e'),
    }
    top, dark, accent = palettes[category]
    accent2 = ('#d65f75', '#75a66a', '#f0d477', '#ae7bb2')[index % 4]
    if category == 'Galletas':
        dessert = f'<circle cx="450" cy="330" r="118" fill="{top}"/><circle cx="450" cy="330" r="105" fill="{accent}"/>' + ''.join(
            f'<circle cx="{385 + (i * 43) % 130}" cy="{270 + (i * 59) % 120}" r="9" fill="{dark}"/>' for i in range(9)
        )
    elif category == 'Brownies':
        dessert = f'<path d="M325 245 L535 245 L590 315 L590 455 L380 455 L325 390Z" fill="{dark}"/><path d="M325 245 L535 245 L590 315 L380 315Z" fill="{top}"/><path d="M380 315 L590 315 L590 455 L380 455Z" fill="{dark}"/><path d="M325 245 L380 315 L380 455 L325 390Z" fill="#6b3d31"/>'
        dessert += ''.join(f'<circle cx="{390 + i * 36}" cy="{280 + (i % 2) * 55}" r="8" fill="{accent2}"/>' for i in range(4))
    elif category == 'Postres en vaso':
        dessert = f'<path d="M350 220 L550 220 L520 475 Q450 505 380 475Z" fill="#ffffff" fill-opacity=".72" stroke="{dark}" stroke-width="8"/><path d="M365 300 L535 300 L528 360 L372 360Z" fill="{top}"/><path d="M372 365 L528 365 L520 420 L380 420Z" fill="{accent}"/><path d="M380 425 L520 425 L515 470 Q450 495 385 470Z" fill="{dark}"/><path d="M345 215 L555 215" stroke="{dark}" stroke-width="10" stroke-linecap="round"/>'
    elif 'Cupcake' in name or 'cupcake' in name.lower():
        dessert = f'<path d="M345 330 L555 330 L520 470 Q450 500 380 470Z" fill="{top}"/><path d="M340 330 Q320 270 370 280 Q380 205 445 250 Q485 185 520 255 Q575 245 560 330Z" fill="{accent}"/><circle cx="450" cy="235" r="19" fill="{accent2}"/>'
    elif category == 'Combos':
        dessert = f'<rect x="310" y="280" width="280" height="180" rx="20" fill="{dark}"/><path d="M310 325 H590" stroke="{accent}" stroke-width="12"/><circle cx="365" cy="270" r="48" fill="{top}"/><circle cx="465" cy="260" r="48" fill="{accent}"/><circle cx="535" cy="285" r="48" fill="{accent2}"/><circle cx="360" cy="270" r="10" fill="{dark}"/><circle cx="465" cy="260" r="10" fill="{dark}"/>'
    else:
        dessert = f'<ellipse cx="450" cy="445" rx="185" ry="38" fill="#e8d8d0"/><path d="M315 365 L585 365 L555 445 Q450 475 345 445Z" fill="{top}"/><path d="M330 315 L570 315 L585 365 L315 365Z" fill="{dark}"/><path d="M355 265 L545 265 L570 315 L330 315Z" fill="{accent}"/><path d="M355 265 Q450 215 545 265" fill="{top}"/><circle cx="450" cy="242" r="18" fill="{accent2}"/>'
        dessert += ''.join(f'<circle cx="{380 + i * 42}" cy="295" r="8" fill="{accent2}"/>' for i in range(3))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="700" viewBox="0 0 900 700" role="img" aria-labelledby="title desc">
<title id="title">{escape(name)}</title><desc id="desc">Ilustración original de postre artesanal de SweetDreams</desc>
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#fff5ed"/><stop offset="1" stop-color="#f8dfe6"/></linearGradient><filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="15" stdDeviation="14" flood-color="#56342c" flood-opacity=".18"/></filter></defs>
<rect width="900" height="700" rx="42" fill="url(#bg)"/><circle cx="140" cy="130" r="58" fill="#fff" fill-opacity=".42"/><circle cx="745" cy="190" r="92" fill="#fff" fill-opacity=".34"/>
<g filter="url(#shadow)">{dessert}</g><text x="450" y="575" text-anchor="middle" fill="#42251f" font-family="Arial,sans-serif" font-size="29" font-weight="700">{escape(name[:32])}</text>
<text x="450" y="620" text-anchor="middle" fill="#8c5c58" font-family="Arial,sans-serif" font-size="16" letter-spacing="4">SWEETDREAMS · HECHO CON AMOR</text></svg>'''


def ensure_artwork():
    image_dir = Path(current_app.root_path) / 'static' / 'img' / 'products'
    image_dir.mkdir(parents=True, exist_ok=True)
    for index, (name, _, _, category) in enumerate(PRODUCTS):
        image_path = image_dir / f'{_slug(name)}.svg'
        if not image_path.exists():
            image_path.write_text(_dessert_svg(name, category, index), encoding='utf-8')


def migrate_recipe_difficulty():
    inspector = inspect(db.engine)
    if 'recipes' not in inspector.get_table_names():
        return
    columns = {column['name'] for column in inspector.get_columns('recipes')}
    if 'difficulty' not in columns:
        db.session.execute(text("ALTER TABLE recipes ADD COLUMN difficulty VARCHAR(20) NOT NULL DEFAULT 'Fácil'"))
        db.session.commit()


def seed_catalog():
    ensure_artwork()
    categories = {}
    for name, description in CATEGORY_DESCRIPTIONS.items():
        category = Category.query.filter_by(name=name).first()
        if category is None:
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.flush()
        categories[name] = category

    for index, (name, description, price, category_name) in enumerate(PRODUCTS):
        product = Product.query.filter_by(name=name).first()
        image = f'/static/img/products/{_slug(name)}.svg'
        if product is None:
            product = Product(
                name=name,
                description=description,
                price=price,
                image=image,
                available=True,
                stock=8 + index % 24,
                category_id=categories[category_name].id,
            )
            db.session.add(product)
        else:
            product.description = description
            product.price = price
            product.image = image
            product.category_id = categories[category_name].id
            if product.stock < 0:
                product.stock = 0
    db.session.flush()

    product_images = {name: f'/static/img/products/{_slug(name)}.svg' for name, _, _, _ in PRODUCTS}
    recipe_image_types = {
        'cookie': 'Galletas Choco Chip',
        'brownie': 'Brownie de Chocolate',
        'jar': 'Postre en Vaso Oreo',
        'cake': 'Pastel de Fresa',
        'tart': 'Tarta de Limón',
        'cupcake': 'Cupcakes Decorados',
    }
    for name, description, ingredients, instructions, prep_time, servings, difficulty, image_type in RECIPES:
        recipe = Recipe.query.filter_by(name=name).first()
        values = {
            'description': description,
            'ingredients': ingredients,
            'instructions': instructions,
            'prep_time': prep_time,
            'servings': servings,
            'difficulty': difficulty,
            'image': product_images[recipe_image_types[image_type]],
        }
        if recipe is None:
            db.session.add(Recipe(name=name, **values))
        else:
            for key, value in values.items():
                setattr(recipe, key, value)
    db.session.commit()
