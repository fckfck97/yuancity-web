from .models import Category
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()
    sub_categories = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'parent_name', 'sub_categories', 'level', 'product_count', 'created_at', 'updated_at']

    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None
    
    def get_sub_categories(self, obj):
        # Solo incluir subcategorías en el detalle, no en listados
        if self.context.get('include_children', False):
            children = obj.children.all()
            return CategorySerializer(children, many=True, context={'include_children': False}).data
        return []
    
    def get_level(self, obj):
        """Determina el nivel de la categoría: 0=raíz (Hombre/Mujer/Niños), 1=categoría, 2=subcategoría"""
        if obj.parent is None:
            return 0
        elif obj.parent.parent is None:
            return 1
        else:
            return 2
    
    def get_product_count(self, obj):
        """Cuenta productos disponibles en esta categoría y sus hijos"""
        from django.db.models import Q, Count
        # Contar productos directos
        count = obj.products.filter(is_available=True).count()
        # Sumar productos de categorías hijas recursivamente
        for child in obj.children.all():
            count += self.get_product_count(child)
        return count

