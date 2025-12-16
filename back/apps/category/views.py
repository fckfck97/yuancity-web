from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.http import Http404
from django.db.models import Count, Q
from .models import Category
from apps.utils.pagination import MediumSetPagination, LargeSetPagination
from .serializers import CategorySerializer
class CategoriesView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            category = self.get_object(kwargs['pk'])
            serializer = CategorySerializer(category, context={'include_children': True})
            return Response(serializer.data)
        else:
            # Filtrar por categoría raíz si se especifica
            root_filter = request.query_params.get('root', None)
            level = request.query_params.get('level', None)
            
            categories = Category.objects.all()
            
            if root_filter:
                # Filtrar por categoría raíz (Hombre/Mujer/Niños)
                try:
                    root_category = Category.objects.get(name__iexact=root_filter, parent=None)
                    # Obtener esta categoría y todos sus descendientes
                    categories = categories.filter(
                        Q(id=root_category.id) | 
                        Q(parent=root_category) | 
                        Q(parent__parent=root_category)
                    )
                except Category.DoesNotExist:
                    return Response({'error': f'Root category "{root_filter}" not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if level is not None:
                # Filtrar por nivel: 0=raíz, 1=categoría, 2=subcategoría
                if level == '0':
                    categories = categories.filter(parent=None)
                elif level == '1':
                    categories = categories.filter(parent__isnull=False, parent__parent=None)
                elif level == '2':
                    categories = categories.filter(parent__parent__isnull=False)
            
            paginator = LargeSetPagination()
            result_page = paginator.paginate_queryset(categories, request)
            serializer = CategorySerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        category = self.get_object(kwargs['pk'])
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ListCategoriesView(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        if not Category.objects.exists():
            return Response({'error': 'No categories found'}, status=status.HTTP_404_NOT_FOUND)

        categories = list(
            Category.objects
            .all()
            .annotate(
                available_products=Count(
                    'products',
                    filter=Q(products__is_available=True)
                )
            )
        )
        if not categories:
            return Response({'error': 'No categories found'}, status=status.HTTP_404_NOT_FOUND)

        children_map = {}
        for category in categories:
            parent_id = category.parent_id
            children_map.setdefault(parent_id, []).append(category)

        def build_node(cat):
            sub_nodes = [build_node(child) for child in children_map.get(cat.id, [])]
            total_products = (cat.available_products or 0) + sum(
                child['product_count'] for child in sub_nodes
            )
            node = {
                'id': cat.id,
                'name': cat.name,
                'product_count': total_products,
                'sub_categories': sub_nodes,
            }
            return node

        result = []
        for root in children_map.get(None, []):
            node = build_node(root)
            result.append(node)

        if not result:
            return Response({'error': 'No categories found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'categories': result}, status=status.HTTP_200_OK)
