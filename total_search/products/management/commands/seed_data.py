from django.core.management.base import BaseCommand
from products.models import Product


SAMPLE_PRODUCTS = [
    {
        "name": "Carrara White Marble Tile",
        "description": "Premium Italian marble tile with white and grey veining.",
        "brand": "StoneWorld",
        "category": "Tiles",
        "price": 2499.00,
        "color": "White",
        "material": "Marble",
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
        "variant_handle": "carrara-white-marble-tile"
    },
    {
        "name": "Teak Wood Flooring Plank",
        "description": "Solid teak hardwood flooring with natural tones.",
        "brand": "WoodCraft",
        "category": "Flooring",
        "price": 1899.00,
        "color": "Brown",
        "material": "Teak Wood",
        "image_url": "https://images.unsplash.com/photo-1582582429416-8d7c9b6b5b5c",
        "variant_handle": "teak-wood-flooring-plank"
    },
    {
        "name": "Royal Blue Ceramic Wall Tile",
        "description": "Glossy blue ceramic tiles for walls.",
        "brand": "CeramicPlus",
        "category": "Tiles",
        "price": 450.00,
        "color": "Blue",
        "material": "Ceramic",
        "image_url": "https://images.unsplash.com/photo-1618220179428-22790b461013",
        "variant_handle": "royal-blue-ceramic-wall-tile"
    },
    {
        "name": "Waterproof Vinyl Plank Flooring",
        "description": "Waterproof vinyl flooring with wood texture.",
        "brand": "FloorPro",
        "category": "Flooring",
        "price": 699.00,
        "color": "Beige",
        "material": "Vinyl",
        "image_url": "https://images.unsplash.com/photo-1598300053653-d6d8d1c8b3c1",
        "variant_handle": "waterproof-vinyl-plank-flooring"
    },
    {
        "name": "Slate Grey Porcelain Floor Tile",
        "description": "Matte grey porcelain tiles.",
        "brand": "TileMax",
        "category": "Tiles",
        "price": 890.00,
        "color": "Grey",
        "material": "Porcelain",
        "image_url": "https://images.unsplash.com/photo-1600607688969-a5bfcd646154",
        "variant_handle": "slate-grey-porcelain-floor-tile"
    },
    {
        "name": "Matte Black Metro Subway Tile",
        "description": "Black subway tiles for modern interiors.",
        "brand": "UrbanTile",
        "category": "Tiles",
        "price": 320.00,
        "color": "Black",
        "material": "Ceramic",
        "image_url": "https://images.unsplash.com/photo-1615874959474-d609969a20ed",
        "variant_handle": "matte-black-metro-subway-tile"
    },
    {
        "name": "Bamboo Engineered Flooring",
        "description": "Eco-friendly bamboo flooring.",
        "brand": "EcoFloor",
        "category": "Flooring",
        "price": 1200.00,
        "color": "Natural",
        "material": "Bamboo",
        "image_url": "https://images.unsplash.com/photo-1600573472592-401b489a3cdc",
        "variant_handle": "bamboo-engineered-flooring"
    },
    {
        "name": "Terracotta Handmade Floor Tile",
        "description": "Handmade terracotta tiles.",
        "brand": "IndiaStone",
        "category": "Tiles",
        "price": 550.00,
        "color": "Orange",
        "material": "Terracotta",
        "image_url": "https://images.unsplash.com/photo-1588854337115-1c67d9247e4d",
        "variant_handle": "terracotta-handmade-floor-tile"
    },
    {
        "name": "Polished Granite Kitchen Counter Tile",
        "description": "Black granite tiles.",
        "brand": "GraniteKing",
        "category": "Tiles",
        "price": 1750.00,
        "color": "Black",
        "material": "Granite",
        "image_url": "https://images.unsplash.com/photo-1592928302636-c83cf1e1b9f5",
        "variant_handle": "polished-granite-kitchen-counter-tile"
    },
    {
        "name": "Herringbone Oak Parquet Flooring",
        "description": "Classic oak parquet flooring.",
        "brand": "WoodCraft",
        "category": "Flooring",
        "price": 2200.00,
        "color": "Honey",
        "material": "Oak Wood",
        "image_url": "https://images.unsplash.com/photo-1560185127-6ed189bf02f4",
        "variant_handle": "herringbone-oak-parquet-flooring"
    },
    {
        "name": "Sage Green Zellige Wall Tile",
        "description": "Handcrafted zellige tiles.",
        "brand": "MoroccoTile",
        "category": "Tiles",
        "price": 1100.00,
        "color": "Green",
        "material": "Zellige Clay",
        "image_url": "https://images.unsplash.com/photo-1599619351208-3e6c839d6828",
        "variant_handle": "sage-green-zellige-wall-tile"
    },
    {
        "name": "Epoxy Resin Self-Leveling Floor",
        "description": "Industrial epoxy flooring.",
        "brand": "FloorPro",
        "category": "Flooring",
        "price": 950.00,
        "color": "Grey",
        "material": "Epoxy Resin",
        "image_url": "https://images.unsplash.com/photo-1581093458791-9f3c3900dfb5",
        "variant_handle": "epoxy-resin-self-leveling-floor"
    },
    {
        "name": "Rustic Wood Look Porcelain Tile",
        "description": "Wood-look porcelain tiles.",
        "brand": "TileMax",
        "category": "Tiles",
        "price": 780.00,
        "color": "Brown",
        "material": "Porcelain",
        "image_url": "https://images.unsplash.com/photo-1604709177225-055f99402ea3",
        "variant_handle": "rustic-wood-look-porcelain-tile"
    },
    {
        "name": "Midnight Blue Mosaic Pool Tile",
        "description": "Glass mosaic pool tiles.",
        "brand": "AquaTile",
        "category": "Tiles",
        "price": 1350.00,
        "color": "Blue",
        "material": "Glass",
        "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
        "variant_handle": "midnight-blue-mosaic-pool-tile"
    },
    {
        "name": "Laminate Flooring Oak Effect",
        "description": "Laminate oak flooring.",
        "brand": "QuickFloor",
        "category": "Flooring",
        "price": 499.00,
        "color": "Brown",
        "material": "Laminate",
        "image_url": "https://images.unsplash.com/photo-1582582494700-1d6a3b89b733",
        "variant_handle": "laminate-flooring-oak-effect"
    }
]

class Command(BaseCommand):
    help = "Seeds 20 sample e-commerce flooring and tile products"

    def handle(self, *args, **kwargs):
        created_count = 0
        skipped_count = 0

        for data in SAMPLE_PRODUCTS:
            product, created = Product.objects.get_or_create(
                variant_handle=data["variant_handle"],
                defaults=data,
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Created: {product.name}")
            else:
                skipped_count += 1
                self.stdout.write(f"  Skipped (exists): {product.name}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Created: {created_count}, Skipped: {skipped_count}"
        ))
        self.stdout.write(
            "Note: post_save signals have auto-indexed all created products into Elasticsearch."
        )