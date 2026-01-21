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
            "subcategorias": [],
        },
        {
            "categoria": "Hombre",
            "subcategorias": [],
        },
        {
            "categoria": "Niños",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # ELECTRÓNICA
    # =========================================================
    "Electrónica": [
        {
            "categoria": "Celulares y Accesorios",
            "subcategorias": [],
        },
        {
            "categoria": "Audio y Video",
            "subcategorias": [],
        },
        {
            "categoria": "Computación (Accesorios)",
            "subcategorias": [],
        },
        {
            "categoria": "Wearables",
            "subcategorias": [],
        },
        {
            "categoria": "Smart Home",
            "subcategorias": [],
        },
        {
            "categoria": "Gaming",
            "subcategorias": [],
        },
        {
            "categoria": "Cámaras y Drones",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # HOGAR Y JARDÍN
    # =========================================================
    "Hogar y Jardín": [
        {
            "categoria": "Decoración",
            "subcategorias": [],
        },
        {
            "categoria": "Cocina y Comedor (Hogar)",
            "subcategorias": [],
        },
        {
            "categoria": "Baño (Hogar)",
            "subcategorias": [],
        },
        {
            "categoria": "Organización y Almacenamiento",
            "subcategorias": [],
        },
        {
            "categoria": "Iluminación",
            "subcategorias": [],
        },
        {
            "categoria": "Jardín y Exteriores",
            "subcategorias": [],
        },
        {
            "categoria": "Limpieza",
            "subcategorias": [],
        },
        {
            "categoria": "Seguridad del Hogar",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # BELLEZA
    # =========================================================
    "Belleza": [
        {
            "categoria": "Maquillaje",
            "subcategorias": [],
        },
        {
            "categoria": "Cuidado de la Piel",
            "subcategorias": [],
        },
        {
            "categoria": "Cuidado del Cabello",
            "subcategorias": [],
        },
        {
            "categoria": "Uñas",
            "subcategorias": [],
        },
        {
            "categoria": "Fragancias",
            "subcategorias": [],
        },
        {
            "categoria": "Cuidado Personal",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # JUGUETES
    # =========================================================
    "Juguetes": [
        {
            "categoria": "Bebés y Primera Infancia",
            "subcategorias": [],
        },
        {
            "categoria": "Muñecas y Accesorios",
            "subcategorias": [],
        },
        {
            "categoria": "Construcción y Bloques",
            "subcategorias": [],
        },
        {
            "categoria": "Vehículos y Radio Control",
            "subcategorias": [],
        },
        {
            "categoria": "Juegos de Mesa y Rompecabezas",
            "subcategorias": [],
        },
        {
            "categoria": "Educativos y STEM",
            "subcategorias": [],
        },
        {
            "categoria": "Figuras y Coleccionables",
            "subcategorias": [],
        },
        {
            "categoria": "Exterior",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # DEPORTES Y AIRE LIBRE
    # =========================================================
    "Deportes y Aire Libre": [
        {
            "categoria": "Fitness y Gimnasio",
            "subcategorias": [],
        },
        {
            "categoria": "Yoga y Pilates",
            "subcategorias": [],
        },
        {
            "categoria": "Ciclismo",
            "subcategorias": [],
        },
        {
            "categoria": "Camping y Senderismo",
            "subcategorias": [],
        },
        {
            "categoria": "Deportes de Equipo",
            "subcategorias": [],
        },
        {
            "categoria": "Natación",
            "subcategorias": [],
        },
        {
            "categoria": "Pesca",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # SALUD
    # =========================================================
    "Salud": [
        {
            "categoria": "Vitaminas y Suplementos",
            "subcategorias": [],
        },
        {
            "categoria": "Monitoreo y Dispositivos",
            "subcategorias": [],
        },
        {
            "categoria": "Primeros Auxilios",
            "subcategorias": [],
        },
        {
            "categoria": "Bienestar",
            "subcategorias": [],
        },
        {
            "categoria": "Ortopedia y Movilidad",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # MASCOTAS
    # =========================================================
    "Mascotas": [
        {
            "categoria": "Perros",
            "subcategorias": [],
        },
        {
            "categoria": "Gatos",
            "subcategorias": [],
        },
        {
            "categoria": "Aves",
            "subcategorias": [],
        },
        {
            "categoria": "Peces y Acuarios",
            "subcategorias": [],
        },
        {
            "categoria": "Pequeños Animales",
            "subcategorias": [],
        },
        {
            "categoria": "Viaje y Transporte",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # PAPELERÍA
    # =========================================================
    "Papelería": [
        {
            "categoria": "Escritura y Corrección",
            "subcategorias": [],
        },
        {
            "categoria": "Cuadernos y Papel",
            "subcategorias": [],
        },
        {
            "categoria": "Arte y Manualidades",
            "subcategorias": [],
        },
        {
            "categoria": "Organización",
            "subcategorias": [],
        },
        {
            "categoria": "Escolar",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # ACCESORIOS DE COCINA
    # =========================================================
    "Accesorios de Cocina": [
        {
            "categoria": "Utensilios",
            "subcategorias": [],
        },
        {
            "categoria": "Gadgets",
            "subcategorias": [],
        },
        {
            "categoria": "Repostería",
            "subcategorias": [],
        },
        {
            "categoria": "Almacenamiento",
            "subcategorias": [],
        },
        {
            "categoria": "Café y Té",
            "subcategorias": [],
        },
        {
            "categoria": "Cuchillos y Afiliado",
            "subcategorias": [],
        },
        {
            "categoria": "Bar y Coctelería",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # JOYERÍA
    # =========================================================
    "Joyería": [
        {
            "categoria": "Piezas",
            "subcategorias": [],
        },
        {
            "categoria": "Relojes",
            "subcategorias": [],
        },
        {
            "categoria": "Material y Estilo",
            "subcategorias": [],
        },
        {
            "categoria": "Accesorios",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # CALZADO
    # =========================================================
    "Calzado": [
        {
            "categoria": "Mujer",
            "subcategorias": [],
        },
        {
            "categoria": "Hombre",
            "subcategorias": [],
        },
        {
            "categoria": "Niños",
            "subcategorias": [],
        },
        {
            "categoria": "Accesorios de calzado",
            "subcategorias": [],
        },
    ],

    # =========================================================
    # ARTÍCULOS DE FIESTA
    # =========================================================
    "Artículos de Fiesta": [
        {
            "categoria": "Decoración",
            "subcategorias": [],
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
