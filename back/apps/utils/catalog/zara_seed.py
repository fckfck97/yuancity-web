# apps/utils/catalog/zara_seed.py
from django.db import transaction
from apps.category.models import Category


MARKETPLACE_CATEGORIES = {
    "root_values": [
        "Ropa",
        "Electrónica",
        "Hogar y Jardín",
        "Belleza",
        "Juguetes",
        "Deportes y Aire Libre",
        "Salud",
        "Mascotas",
        "Papelería",
        "Accesorios de Cocina",
        "Joyería",
        "Calzado",
        "Artículos de Fiesta",
        "Herramientas",
        "Cuidado del Automóvil",
        "Tecnología de la Información",
        "Ropa de Cama y Baño",
        "Artículos de Viaje",
        "Artículos de Oficina",
        "Cosas al azar",
    ],

    # =========================================================
    # ROPA
    # =========================================================
    "Ropa": [
        {
            "categoria": "Mujer",
            "subcategorias": [
                "Abrigos y chaquetas",
                "Blazers y trajes",
                "Vestidos",
                "Monos y enterizos",
                "Tops y camisetas",
                "Camisas y blusas",
                "Sudaderas y hoodies",
                "Punto (suéteres y cárdigans)",
                "Pantalones",
                "Jeans",
                "Faldas",
                "Shorts y bermudas",
                "Ropa deportiva",
                "Ropa interior",
                "Pijamas y loungewear",
                "Ropa de baño",
                "Accesorios de moda (bufandas, gorras, cinturones)",
            ],
        },
        {
            "categoria": "Hombre",
            "subcategorias": [
                "Abrigos y chaquetas",
                "Blazers y trajes",
                "Camisas",
                "Camisetas",
                "Polos",
                "Sudaderas y hoodies",
                "Punto (suéteres y cárdigans)",
                "Pantalones",
                "Jeans",
                "Chinos",
                "Joggers",
                "Shorts y bermudas",
                "Ropa deportiva",
                "Ropa interior",
                "Pijamas y loungewear",
                "Ropa de baño",
                "Accesorios de moda (gorras, cinturones, bufandas)",
            ],
        },
        {
            "categoria": "Niños",
            "subcategorias": [
                "Bebé (0-24m)",
                "Niña (2-12)",
                "Niño (2-12)",
                "Ropa escolar",
                "Abrigos y chaquetas",
                "Camisetas y tops",
                "Pantalones y jeans",
                "Vestidos (niña)",
                "Conjuntos",
                "Pijamas",
                "Ropa interior",
                "Ropa deportiva",
                "Ropa de baño",
                "Accesorios infantiles (gorros, bufandas, mochilas)",
            ],
        },
    ],

    # =========================================================
    # ELECTRÓNICA
    # =========================================================
    "Electrónica": [
        {
            "categoria": "Celulares y Accesorios",
            "subcategorias": [
                "Fundas y protectores",
                "Protectores de pantalla",
                "Cargadores y adaptadores",
                "Cables",
                "Power banks",
                "Soportes (auto/escritorio)",
                "Auriculares (in-ear/over-ear)",
                "Bluetooth (receptores/transmisores)",
            ],
        },
        {
            "categoria": "Audio y Video",
            "subcategorias": [
                "Parlantes",
                "Soundbars",
                "Micrófonos",
                "Proyectores",
                "Streaming devices",
                "Accesorios de TV",
                "Accesorios de video (capturadoras, cables)",
            ],
        },
        {
            "categoria": "Computación (Accesorios)",
            "subcategorias": [
                "Teclados",
                "Mouse",
                "Mousepads",
                "Webcams",
                "Hubs USB y docks",
                "Adaptadores (HDMI/USB-C)",
                "Monitores (accesorios)",
                "Soportes de laptop/monitor",
            ],
        },
        {
            "categoria": "Wearables",
            "subcategorias": [
                "Smartwatches",
                "Bandas deportivas",
                "Accesorios para wearables (correas, cargadores)",
            ],
        },
        {
            "categoria": "Smart Home",
            "subcategorias": [
                "Cámaras de seguridad",
                "Bombillos inteligentes",
                "Enchufes inteligentes",
                "Sensores (movimiento/puerta)",
                "Timbres inteligentes",
                "Cerraduras inteligentes",
            ],
        },
        {
            "categoria": "Gaming",
            "subcategorias": [
                "Controles y mandos",
                "Accesorios para consola",
                "Accesorios para PC gamer",
                "Headsets gamer",
                "Sillas gamer (accesorios)",
            ],
        },
        {
            "categoria": "Cámaras y Drones",
            "subcategorias": [
                "Cámaras de acción",
                "Drones",
                "Gimbals y estabilizadores",
                "Trípodes",
                "Baterías y accesorios",
            ],
        },
    ],

    # =========================================================
    # HOGAR Y JARDÍN
    # =========================================================
    "Hogar y Jardín": [
        {
            "categoria": "Decoración",
            "subcategorias": [
                "Cuadros y arte mural",
                "Espejos",
                "Relojes decorativos",
                "Jarrones y floreros",
                "Velas y aromatizantes",
                "Alfombras",
                "Cortinas",
                "Cojines y fundas",
            ],
        },
        {
            "categoria": "Cocina y Comedor (Hogar)",
            "subcategorias": [
                "Vajilla y cristalería",
                "Contenedores y almacenamiento",
                "Textiles (manteles, paños)",
                "Accesorios de mesa",
            ],
        },
        {
            "categoria": "Baño (Hogar)",
            "subcategorias": [
                "Organización de baño",
                "Accesorios (dispensadores, jaboneras)",
                "Cortinas de baño",
                "Tapetes de baño",
            ],
        },
        {
            "categoria": "Organización y Almacenamiento",
            "subcategorias": [
                "Cajas y canastas",
                "Organizadores de clóset",
                "Estanterías (accesorios)",
                "Ganchos y colgadores",
                "Organizadores de cocina",
            ],
        },
        {
            "categoria": "Iluminación",
            "subcategorias": [
                "Lámparas de mesa",
                "Lámparas de pie",
                "Luces LED decorativas",
                "Guirnaldas de luz",
                "Accesorios de iluminación",
            ],
        },
        {
            "categoria": "Jardín y Exteriores",
            "subcategorias": [
                "Macetas y jardineras",
                "Riego (mangueras, aspersores)",
                "Decoración exterior",
                "Muebles de exterior (accesorios)",
                "Parrillas y BBQ (accesorios)",
            ],
        },
        {
            "categoria": "Limpieza",
            "subcategorias": [
                "Guantes y esponjas",
                "Paños y microfibras",
                "Organizadores de limpieza",
                "Accesorios para aspiradora",
            ],
        },
        {
            "categoria": "Seguridad del Hogar",
            "subcategorias": [
                "Cajas fuertes",
                "Cerraduras (no inteligentes)",
                "Alarmas básicas",
                "Sensores básicos",
            ],
        },
    ],

    # =========================================================
    # BELLEZA
    # =========================================================
    "Belleza": [
        {
            "categoria": "Maquillaje",
            "subcategorias": [
                "Rostro (base, corrector, polvos)",
                "Ojos (sombras, delineadores, máscara)",
                "Labios (labiales, gloss, bálsamos)",
                "Brochas y esponjas",
                "Sets de maquillaje",
            ],
        },
        {
            "categoria": "Cuidado de la Piel",
            "subcategorias": [
                "Limpieza facial",
                "Hidratación",
                "Sérums y tratamientos",
                "Mascarillas",
                "Protector solar",
                "Cuidado corporal",
            ],
        },
        {
            "categoria": "Cuidado del Cabello",
            "subcategorias": [
                "Shampoo y acondicionador",
                "Mascarillas y tratamientos",
                "Styling (geles, ceras, sprays)",
                "Herramientas (secadores, planchas)",
                "Accesorios (peines, cepillos)",
            ],
        },
        {
            "categoria": "Uñas",
            "subcategorias": [
                "Esmaltes",
                "Kits de manicura",
                "Uñas postizas",
                "Lámparas UV",
                "Accesorios (limas, cortaúñas)",
            ],
        },
        {
            "categoria": "Fragancias",
            "subcategorias": [
                "Perfumes",
                "Body mist",
                "Sets de fragancia",
            ],
        },
        {
            "categoria": "Cuidado Personal",
            "subcategorias": [
                "Afeitado y depilación",
                "Desodorantes",
                "Higiene íntima (general)",
                "Cuidado dental",
            ],
        },
    ],

    # =========================================================
    # JUGUETES
    # =========================================================
    "Juguetes": [
        {
            "categoria": "Bebés y Primera Infancia",
            "subcategorias": [
                "Sonajeros",
                "Mordedores",
                "Juguetes sensoriales",
                "Tapetes de juego",
            ],
        },
        {
            "categoria": "Muñecas y Accesorios",
            "subcategorias": [
                "Muñecas",
                "Coches y cunas (accesorios)",
                "Ropa para muñecas",
            ],
        },
        {
            "categoria": "Construcción y Bloques",
            "subcategorias": [
                "Bloques",
                "Sets de construcción",
                "Pistas y circuitos",
            ],
        },
        {
            "categoria": "Vehículos y Radio Control",
            "subcategorias": [
                "Carros a control remoto",
                "Drones para niños",
                "Pistas y accesorios",
            ],
        },
        {
            "categoria": "Juegos de Mesa y Rompecabezas",
            "subcategorias": [
                "Juegos familiares",
                "Cartas",
                "Rompecabezas",
            ],
        },
        {
            "categoria": "Educativos y STEM",
            "subcategorias": [
                "Kits de ciencia",
                "Robótica básica",
                "Juguetes didácticos",
            ],
        },
        {
            "categoria": "Figuras y Coleccionables",
            "subcategorias": [
                "Figuras de acción",
                "Coleccionables",
                "Sets temáticos",
            ],
        },
        {
            "categoria": "Exterior",
            "subcategorias": [
                "Juegos de agua",
                "Cometas",
                "Pelotas y juegos al aire libre",
            ],
        },
    ],

    # =========================================================
    # DEPORTES Y AIRE LIBRE
    # =========================================================
    "Deportes y Aire Libre": [
        {
            "categoria": "Fitness y Gimnasio",
            "subcategorias": [
                "Bandas elásticas",
                "Mancuernas y pesas",
                "Esterillas",
                "Accesorios de entrenamiento",
            ],
        },
        {
            "categoria": "Yoga y Pilates",
            "subcategorias": [
                "Mat de yoga",
                "Bloques y straps",
                "Ropa de yoga",
            ],
        },
        {
            "categoria": "Ciclismo",
            "subcategorias": [
                "Cascos",
                "Luces",
                "Guantes",
                "Soportes y accesorios",
            ],
        },
        {
            "categoria": "Camping y Senderismo",
            "subcategorias": [
                "Carpas",
                "Linternas",
                "Mochilas",
                "Sacos de dormir",
                "Accesorios de camping",
            ],
        },
        {
            "categoria": "Deportes de Equipo",
            "subcategorias": [
                "Fútbol",
                "Baloncesto",
                "Voleibol",
                "Accesorios (balones, redes)",
            ],
        },
        {
            "categoria": "Natación",
            "subcategorias": [
                "Gafas",
                "Gorros",
                "Accesorios",
                "Ropa de baño deportiva",
            ],
        },
        {
            "categoria": "Pesca",
            "subcategorias": [
                "Cañas",
                "Señuelos",
                "Cajas y organización",
                "Accesorios",
            ],
        },
    ],

    # =========================================================
    # SALUD
    # =========================================================
    "Salud": [
        {
            "categoria": "Vitaminas y Suplementos",
            "subcategorias": [
                "Multivitamínicos",
                "Proteína y fitness",
                "Omega 3",
                "Colágeno",
                "Minerales",
            ],
        },
        {
            "categoria": "Monitoreo y Dispositivos",
            "subcategorias": [
                "Tensiómetros",
                "Termómetros",
                "Oxímetros",
                "Básculas",
            ],
        },
        {
            "categoria": "Primeros Auxilios",
            "subcategorias": [
                "Botiquines",
                "Vendas y gasas",
                "Antisépticos (general)",
                "Accesorios",
            ],
        },
        {
            "categoria": "Bienestar",
            "subcategorias": [
                "Masajeadores",
                "Aromaterapia",
                "Relajación (accesorios)",
            ],
        },
        {
            "categoria": "Ortopedia y Movilidad",
            "subcategorias": [
                "Soportes y braces",
                "Plantillas",
                "Accesorios de movilidad",
            ],
        },
    ],

    # =========================================================
    # MASCOTAS
    # =========================================================
    "Mascotas": [
        {
            "categoria": "Perros",
            "subcategorias": [
                "Alimento",
                "Camas y casas",
                "Juguetes",
                "Correas y arneses",
                "Higiene y grooming",
                "Ropa para perro",
            ],
        },
        {
            "categoria": "Gatos",
            "subcategorias": [
                "Alimento",
                "Areneros y arena",
                "Rascadores",
                "Juguetes",
                "Camas",
                "Higiene",
            ],
        },
        {
            "categoria": "Aves",
            "subcategorias": [
                "Jaulas",
                "Alimento",
                "Accesorios",
            ],
        },
        {
            "categoria": "Peces y Acuarios",
            "subcategorias": [
                "Acuarios",
                "Filtros",
                "Alimento",
                "Decoración",
            ],
        },
        {
            "categoria": "Pequeños Animales",
            "subcategorias": [
                "Hámsters y roedores",
                "Accesorios y hábitat",
                "Alimento",
            ],
        },
        {
            "categoria": "Viaje y Transporte",
            "subcategorias": [
                "Guacales y transportadoras",
                "Accesorios de carro",
                "Bebederos portátiles",
            ],
        },
    ],

    # =========================================================
    # PAPELERÍA
    # =========================================================
    "Papelería": [
        {
            "categoria": "Escritura y Corrección",
            "subcategorias": [
                "Bolígrafos",
                "Lápices",
                "Marcadores",
                "Resaltadores",
                "Correctores",
            ],
        },
        {
            "categoria": "Cuadernos y Papel",
            "subcategorias": [
                "Cuadernos",
                "Libretas",
                "Agendas",
                "Hojas y resmas",
                "Papel fotográfico",
            ],
        },
        {
            "categoria": "Arte y Manualidades",
            "subcategorias": [
                "Pinturas",
                "Pinceles",
                "Pegantes",
                "Tijeras y cutters",
                "Foamy y cartulina",
                "Scrapbooking (básico)",
            ],
        },
        {
            "categoria": "Organización",
            "subcategorias": [
                "Carpetas",
                "Archivadores",
                "Separadores",
                "Post-it",
                "Etiquetas",
            ],
        },
        {
            "categoria": "Escolar",
            "subcategorias": [
                "Estuches",
                "Reglas y escuadras",
                "Calculadoras",
                "Morrales escolares (básico)",
            ],
        },
    ],

    # =========================================================
    # ACCESORIOS DE COCINA
    # =========================================================
    "Accesorios de Cocina": [
        {
            "categoria": "Utensilios",
            "subcategorias": [
                "Espátulas",
                "Pinzas",
                "Cucharones",
                "Batidores",
                "Tablas de picar",
            ],
        },
        {
            "categoria": "Gadgets",
            "subcategorias": [
                "Peladores",
                "Ralladores",
                "Cortadores",
                "Prensas y exprimidores",
                "Termómetros de cocina",
            ],
        },
        {
            "categoria": "Repostería",
            "subcategorias": [
                "Moldes",
                "Cortadores de galleta",
                "Mangas pasteleras",
                "Accesorios de decoración",
            ],
        },
        {
            "categoria": "Almacenamiento",
            "subcategorias": [
                "Recipientes",
                "Bolsas reutilizables",
                "Frascos",
                "Organizadores de despensa",
            ],
        },
        {
            "categoria": "Café y Té",
            "subcategorias": [
                "Filtros",
                "Prensas",
                "Molinillos (manuales)",
                "Teteras y accesorios",
            ],
        },
        {
            "categoria": "Cuchillos y Afiliado",
            "subcategorias": [
                "Cuchillos",
                "Afiladores",
                "Tacos y fundas",
            ],
        },
        {
            "categoria": "Bar y Coctelería",
            "subcategorias": [
                "Cocteleras",
                "Medidores",
                "Abridores",
                "Accesorios de vino",
            ],
        },
    ],

    # =========================================================
    # JOYERÍA
    # =========================================================
    "Joyería": [
        {
            "categoria": "Piezas",
            "subcategorias": [
                "Aretes",
                "Collares",
                "Pulseras",
                "Anillos",
                "Sets",
            ],
        },
        {
            "categoria": "Relojes",
            "subcategorias": [
                "Relojes (hombre)",
                "Relojes (mujer)",
                "Correas y accesorios",
            ],
        },
        {
            "categoria": "Material y Estilo",
            "subcategorias": [
                "Joyería fina (plata/oro)",
                "Bisutería",
                "Acero inoxidable",
                "Perlas y piedras",
            ],
        },
        {
            "categoria": "Accesorios",
            "subcategorias": [
                "Joyeros y estuches",
                "Piercings",
                "Accesorios para el cabello (clips, diademas)",
            ],
        },
    ],

    # =========================================================
    # CALZADO
    # =========================================================
    "Calzado": [
        {
            "categoria": "Mujer",
            "subcategorias": [
                "Zapatillas (sneakers)",
                "Tacones",
                "Botas y botines",
                "Sandalias",
                "Bailarinas y flats",
                "Mocasines",
            ],
        },
        {
            "categoria": "Hombre",
            "subcategorias": [
                "Zapatillas (sneakers)",
                "Zapatos formales",
                "Botas",
                "Sandalias",
                "Mocasines",
            ],
        },
        {
            "categoria": "Niños",
            "subcategorias": [
                "Escolar",
                "Zapatillas",
                "Botas",
                "Sandalias",
            ],
        },
        {
            "categoria": "Accesorios de calzado",
            "subcategorias": [
                "Plantillas",
                "Cordones",
                "Cuidado del calzado",
            ],
        },
    ],

    # =========================================================
    # ARTÍCULOS DE FIESTA
    # =========================================================
    "Artículos de Fiesta": [
        {
            "categoria": "Decoración",
            "subcategorias": [
                "Globos",
                "Guirnaldas",
                "Banners",
                "Centros de mesa",
                "Fondos para fotos",
            ],
        },
        {
            "categoria": "Desechables",
            "subcategorias": [
                "Platos",
                "Vasos",
                "Servilletas",
                "Cubiertos",
                "Manteles",
            ],
        },
        {
            "categoria": "Disfraces y Accesorios",
            "subcategorias": [
                "Disfraces",
                "Máscaras",
                "Sombreros y accesorios",
                "Maquillaje de fiesta (básico)",
            ],
        },
        {
            "categoria": "Repostería de Fiesta",
            "subcategorias": [
                "Velas",
                "Topper y decoración",
                "Cápsulas y moldes",
            ],
        },
        {
            "categoria": "Piñatas y Juegos",
            "subcategorias": [
                "Piñatas",
                "Rellenos",
                "Juegos de fiesta",
            ],
        },
        {
            "categoria": "Regalos y Envolturas",
            "subcategorias": [
                "Bolsas de regalo",
                "Papel de regalo",
                "Tarjetas",
                "Cintas",
            ],
        },
    ],

    # =========================================================
    # HERRAMIENTAS
    # =========================================================
    "Herramientas": [
        {
            "categoria": "Herramientas Manuales",
            "subcategorias": [
                "Destornilladores",
                "Llaves y dados",
                "Alicates",
                "Martillos",
                "Sierras manuales",
            ],
        },
        {
            "categoria": "Herramientas Eléctricas",
            "subcategorias": [
                "Taladros",
                "Sierras",
                "Lijadoras",
                "Atornilladores eléctricos",
                "Accesorios (baterías/cargadores)",
            ],
        },
        {
            "categoria": "Medición y Marcado",
            "subcategorias": [
                "Cintas métricas",
                "Niveles",
                "Escuadras",
                "Calibradores",
            ],
        },
        {
            "categoria": "Consumibles y Accesorios",
            "subcategorias": [
                "Brocas",
                "Discos de corte",
                "Lijas",
                "Tornillería (básico)",
                "Cintas y selladores (básico)",
            ],
        },
        {
            "categoria": "Seguridad",
            "subcategorias": [
                "Guantes",
                "Gafas",
                "Mascarillas",
                "Protectores auditivos",
            ],
        },
        {
            "categoria": "Organización de Taller",
            "subcategorias": [
                "Cajas de herramientas",
                "Maletines",
                "Organizadores",
            ],
        },
    ],

    # =========================================================
    # CUIDADO DEL AUTOMÓVIL
    # =========================================================
    "Cuidado del Automóvil": [
        {
            "categoria": "Interior",
            "subcategorias": [
                "Fundas y cubreasientos",
                "Organizadores",
                "Soportes para celular",
                "Ambientadores",
                "Tapetes",
            ],
        },
        {
            "categoria": "Exterior",
            "subcategorias": [
                "Cobertores",
                "Accesorios de carrocería (básico)",
                "Limpiaparabrisas",
                "Stickers (básico)",
            ],
        },
        {
            "categoria": "Electrónica y Accesorios",
            "subcategorias": [
                "Cargadores para carro",
                "Luces LED",
                "Cámaras (dashcam/reversa)",
                "Sensores (parqueo)",
            ],
        },
        {
            "categoria": "Limpieza y Detailing",
            "subcategorias": [
                "Shampoo y limpiadores (general)",
                "Microfibras",
                "Cepillos",
                "Accesorios de aspirado",
            ],
        },
        {
            "categoria": "Mantenimiento (Básico)",
            "subcategorias": [
                "Compresores portátiles",
                "Cables pasa-corriente",
                "Medidores (presión/básico)",
                "Accesorios varios",
            ],
        },
    ],

    # =========================================================
    # TECNOLOGÍA DE LA INFORMACIÓN
    # =========================================================
    "Tecnología de la Información": [
        {
            "categoria": "Computadores",
            "subcategorias": [
                "Portátiles",
                "PC de escritorio",
                "Mini PC",
                "All-in-One",
            ],
        },
        {
            "categoria": "Componentes",
            "subcategorias": [
                "Procesadores (CPU)",
                "Tarjetas gráficas (GPU)",
                "Memoria RAM",
                "SSD y HDD",
                "Motherboards",
                "Fuentes de poder",
                "Cajas (cases)",
                "Refrigeración (cooling)",
            ],
        },
        {
            "categoria": "Periféricos",
            "subcategorias": [
                "Monitores",
                "Teclados",
                "Mouse",
                "Impresoras",
                "Escáneres",
                "Webcams",
            ],
        },
        {
            "categoria": "Redes",
            "subcategorias": [
                "Routers",
                "Switches",
                "Repetidores",
                "Cables de red",
            ],
        },
        {
            "categoria": "Almacenamiento",
            "subcategorias": [
                "Discos externos",
                "Memorias USB",
                "Tarjetas microSD/SD",
                "NAS (básico)",
            ],
        },
        {
            "categoria": "Energía y Protección",
            "subcategorias": [
                "UPS",
                "Reguladores",
                "Supresores de pico",
            ],
        },
    ],

    # =========================================================
    # ROPA DE CAMA Y BAÑO
    # =========================================================
    "Ropa de Cama y Baño": [
        {
            "categoria": "Ropa de Cama",
            "subcategorias": [
                "Sábanas",
                "Fundas de almohada",
                "Edredones",
                "Cobijas y mantas",
                "Protectores de colchón",
            ],
        },
        {
            "categoria": "Baño",
            "subcategorias": [
                "Toallas",
                "Albornoces",
                "Tapetes de baño",
                "Cortinas de baño",
            ],
        },
        {
            "categoria": "Textiles del Hogar",
            "subcategorias": [
                "Cojines y fundas",
                "Manteles",
                "Paños de cocina",
                "Cortinas (básico)",
            ],
        },
    ],

    # =========================================================
    # ARTÍCULOS DE VIAJE
    # =========================================================
    "Artículos de Viaje": [
        {
            "categoria": "Maletas y Equipaje",
            "subcategorias": [
                "Maletas de cabina",
                "Maletas grandes",
                "Sets de maletas",
                "Bolsos de viaje",
            ],
        },
        {
            "categoria": "Mochilas",
            "subcategorias": [
                "Mochilas de viaje",
                "Mochilas para portátil",
                "Mochilas plegables",
            ],
        },
        {
            "categoria": "Organización",
            "subcategorias": [
                "Packing cubes",
                "Neceser y cosmetiqueras",
                "Bolsas de compresión",
                "Portadocumentos",
            ],
        },
        {
            "categoria": "Accesorios",
            "subcategorias": [
                "Candados",
                "Básculas para equipaje",
                "Etiquetas",
                "Almohadas de cuello",
                "Tapaojos y antifaces",
            ],
        },
        {
            "categoria": "Adaptadores y Carga",
            "subcategorias": [
                "Adaptadores universales",
                "Cargadores de viaje",
                "Organizadores de cables",
            ],
        },
        {
            "categoria": "Seguridad",
            "subcategorias": [
                "Billeteras RFID (básico)",
                "Riñoneras de seguridad",
                "Fundas impermeables",
            ],
        },
    ],

    # =========================================================
    # ARTÍCULOS DE OFICINA
    # =========================================================
    "Artículos de Oficina": [
        {
            "categoria": "Mobiliario",
            "subcategorias": [
                "Sillas",
                "Escritorios",
                "Soportes y bases",
                "Reposapiés",
            ],
        },
        {
            "categoria": "Organización",
            "subcategorias": [
                "Archivadores",
                "Bandejas",
                "Cajas",
                "Separadores",
                "Organizadores de escritorio",
            ],
        },
        {
            "categoria": "Impresión y Consumibles",
            "subcategorias": [
                "Papel",
                "Etiquetas",
                "Cartuchos y tóner (general)",
            ],
        },
        {
            "categoria": "Tecnología para Oficina",
            "subcategorias": [
                "Audífonos",
                "Webcams",
                "Hubs y adaptadores",
                "Soportes para laptop",
            ],
        },
        {
            "categoria": "Pizarras y Señalización",
            "subcategorias": [
                "Pizarras",
                "Marcadores",
                "Accesorios",
            ],
        },
        {
            "categoria": "Ergonomía",
            "subcategorias": [
                "Soportes de monitor",
                "Apoyamuñecas",
                "Cojines lumbares",
            ],
        },
    ],

    # =========================================================
    # COSAS AL AZAR
    # =========================================================
    "Cosas al azar": [
        {
            "categoria": "Regalos y Novedades",
            "subcategorias": [
                "Regalos creativos",
                "Detalles románticos",
                "Sorpresas",
            ],
        },
        {
            "categoria": "Gadgets Curiosos",
            "subcategorias": [
                "Mini herramientas",
                "Accesorios virales",
                "Gadgets de escritorio",
            ],
        },
        {
            "categoria": "Coleccionables",
            "subcategorias": [
                "Figuras",
                "Stickers y pins",
                "Cartas y memorabilia (básico)",
            ],
        },
        {
            "categoria": "Kits y Manualidades",
            "subcategorias": [
                "Kits DIY",
                "Kits de pintura",
                "Kits de decoración",
            ],
        },
        {
            "categoria": "Hogar Ingenioso",
            "subcategorias": [
                "Soluciones compactas",
                "Organizadores raros",
                "Accesorios multiuso",
            ],
        },
    ],

    "recomendaciones_de_normalizacion": {
        "nombres": "usar singular consistente y títulos cortos",
        "evitar_duplicados": "no repetir subcategorías entre categorías (p. ej. calzado solo en 'Calzado')",
    },
}


def seed_zara_categories(purge_roots: bool = False):
    """
    Reemplazo del seed anterior (Zara) por un catálogo marketplace.

    Árbol:
      Categoría raíz (nivel 1)
        -> bloque (nivel 2)
            -> subcategoría (nivel 3)

    Idempotente: usa get_or_create.
    Opcional: purge_roots=True elimina SOLO las raíces del catálogo y sus hijos (cuidado si ya hay productos enlazados).
    """
    root_values = MARKETPLACE_CATEGORIES.get("root_values", [])

    with transaction.atomic():
        if purge_roots:
            # IMPORTANTE: esto borrará en cascada hijos; úsalo solo si estás seguro.
            Category.objects.filter(parent=None, name__in=root_values).delete()

        for root_name in root_values:
            bloques = MARKETPLACE_CATEGORIES.get(root_name, [])

            # nivel 1: categoría raíz
            root_cat, _ = Category.objects.get_or_create(
                parent=None,
                name=root_name,
            )

            for bloque in bloques:
                nombre_bloque = bloque.get("categoria")
                subcategorias = bloque.get("subcategorias", [])

                if not nombre_bloque:
                    continue

                # nivel 2: bloque
                bloque_cat, _ = Category.objects.get_or_create(
                    parent=root_cat,
                    name=nombre_bloque,
                )

                # nivel 3: subcategorías
                for sub_name in subcategorias:
                    if not sub_name:
                        continue

                    Category.objects.get_or_create(
                        parent=bloque_cat,
                        name=sub_name,
                    )


# Alias opcional por si ya llamabas a otra función desde un comando/fixture
seed_marketplace_categories = seed_zara_categories
