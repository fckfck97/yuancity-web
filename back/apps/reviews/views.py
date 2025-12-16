from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from apps.product.models import Product
from apps.orders.models import Order, OrderItem
from .models import Review

FEEDBACK_OPTIONS = {
    "packaging": "Buen empaque",
    "content": "Buen contenido",
    "surprise": "Te sorprendió",
    "ontime": "Llegó a tiempo",
    "recommend": "Lo recomendarías",
}


def _sanitize_extras(raw):
    if not raw:
        return []
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, (list, tuple)):
        return []
    normalized = []
    for value in raw:
        key = str(value)
        if key in FEEDBACK_OPTIONS and key not in normalized:
            normalized.append(key)
    return normalized


def _format_extras(extras):
    formatted = []
    for key in extras or []:
        formatted.append(
            {
                "key": key,
                "label": FEEDBACK_OPTIONS.get(key, key),
            }
        )
    return formatted


def _serialize_review(review):
    return {
        "id": review.id,
        "rating": review.rating,
        "comment": review.comment,
        "date_created": review.date_created,
        "user": review.user.first_name,
        "extra_feedback": _format_extras(review.extra_feedback),
    }

class GetProductReviewsView(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, productId, format=None):
        try:
            product_id = productId
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            product = Product.objects.get(id=product_id)

            results = []

            if Review.objects.filter(product=product).exists():
                reviews = Review.objects.order_by(
                    '-date_created'
                ).filter(product=product)

                for review in reviews:
                    results.append(_serialize_review(review))
            
            return Response(
                {'reviews': results},
                status=status.HTTP_200_OK
            )

        except:
            return Response(
                {'error': 'Something went wrong when retrieving reviews'},
                status=status.HTTP_404_NOT_FOUND
            )
    

class GetProductReviewView(APIView):
    def get(self, request, productId, format=None):
        user = self.request.user

        try:
            product_id = productId
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product = Product.objects.get(id=product_id)

            result = {}

            if Review.objects.filter(user=user, product=product).exists():
                review = Review.objects.get(user=user, product=product)

                result = _serialize_review(review)

            return Response(
                {'review': result},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Something went wrong when retrieving review'},
                status=status.HTTP_404_NOT_FOUND
            )


class CreateProductReviewView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        order_item_id = data.get('order_item_id')
        if not order_item_id:
            return Response(
                {'error': 'order_item_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rating = float(data['rating'])
        except:
            return Response(
                {'error': 'Rating must be a decimal value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            comment = str(data['comment'])
        except:
            return Response(
                {'error': 'Must pass a comment when creating review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if not Product.objects.filter(id=productId).exists():
                return Response(
                    {'error': 'This Product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product = Product.objects.get(id=productId)

            try:
                order_item = OrderItem.objects.select_related('order', 'product').get(id=order_item_id)
            except OrderItem.DoesNotExist:
                return Response(
                    {'error': 'El item de pedido no existe'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if order_item.order.user != user:
                return Response(
                    {'error': 'No puedes reseñar este pedido'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if order_item.product != product:
                return Response(
                    {'error': 'El producto no coincide con el pedido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if order_item.order.status != Order.OrderStatus.delivered:
                return Response(
                    {'error': 'Solo puedes reseñar pedidos completados'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Review.objects.filter(order_item=order_item).exists():
                return Response(
                    {'error': 'Ya calificaste este pedido'},
                    status=status.HTTP_409_CONFLICT
                )

            review = Review.objects.create(
                user=user,
                product=product,
                rating=rating,
                comment=comment,
                order_item=order_item,
                extra_feedback=_sanitize_extras(data.get('extras'))
            )

            result = _serialize_review(review)
            results = [
                _serialize_review(r)
                for r in Review.objects.order_by('-date_created').filter(product=product)
            ]

            return Response(
                {'review': result, 'reviews': results},
                status=status.HTTP_201_CREATED
            )
        except:
            return Response(
                {'error': 'Something went wrong when creating review'},
                status=status.HTTP_404_NOT_FOUND
            )

        

class UpdateProductReviewView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        try:
            product_id = productId
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            rating = float(data['rating'])
        except:
            return Response(
                {'error': 'Rating must be a decimal value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            comment = str(data['comment'])
        except:
            return Response(
                {'error': 'Must pass a comment when creating review'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product = Product.objects.get(id=product_id)

            if not Review.objects.filter(user=user, product=product).exists():
                return Response(
                    {'error': 'Review for this product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            Review.objects.filter(user=user, product=product).update(
                rating=rating,
                comment=comment,
                extra_feedback=_sanitize_extras(data.get('extras')),
            )

            review = Review.objects.get(user=user, product=product)

            result = _serialize_review(review)
            results = [
                _serialize_review(r)
                for r in Review.objects.order_by('-date_created').filter(product=product)
            ]

            return Response(
                {'review': result, 'reviews': results},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Something went wrong when updating review'},
                status=status.HTTP_404_NOT_FOUND
            )


class DeleteProductReviewView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def delete(self, request, productId, format=None):
        user = self.request.user

        try:
            product_id = productId
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product = Product.objects.get(id=product_id)

            results = []

            if Review.objects.filter(user=user, product=product).exists():
                Review.objects.filter(user=user, product=product).delete()

                reviews = Review.objects.order_by('-date_created').filter(
                    product=product
                )

                for review in reviews:
                    results.append(_serialize_review(review))

                return Response(
                    {'reviews': results},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Review for this product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except:
            return Response(
                {'error': 'Something went wrong when deleting product review'},
                status=status.HTTP_404_NOT_FOUND
            )


class FilterProductReviewsView(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, productId, format=None):
        try:
            product_id = productId
        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not Product.objects.filter(id=product_id).exists():
            return Response(
                {'error': 'This product does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        product = Product.objects.get(id=product_id)

        rating = request.query_params.get('rating')

        try:
            rating = float(rating)
        except:
            return Response(
                {'error': 'Rating must be a decimal value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if not rating:
                rating = 5.0
            elif rating > 5.0:
                rating = 5.0
            elif rating < 0.5:
                rating = 0.5

            results = []

            if Review.objects.filter(product=product).exists():
                if rating == 0.5:
                    reviews = Review.objects.order_by('-date_created').filter(
                        rating=rating, product=product
                    )
                else:
                    reviews = Review.objects.order_by('-date_created').filter(
                        rating__lte=rating,
                        product=product
                    ).filter(
                        rating__gte=(rating - 0.5),
                        product=product
                    )

                for review in reviews:
                    results.append(_serialize_review(review))

            return Response(
                {'reviews': results},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Something went wrong when filtering reviews for product'},
                status=status.HTTP_404_NOT_FOUND
            )


class PendingReviewsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        pending_items = (
            OrderItem.objects
            .select_related('order', 'product')
            .filter(order__user=user, order__status=Order.OrderStatus.delivered)
            .exclude(review__isnull=False)
            .order_by('-order__date_issued')
        )

        results = []
        for item in pending_items:
            results.append({
                "order_item_id": str(item.id),
                "product_id": str(item.product.id),
                "product_name": item.product.name,
                "product_price": str(item.product.price),
                "order_id": str(item.order.id),
                "transaction_id": str(item.order.transaction_id),
                "date_issued": item.order.date_issued,
            })

        return Response({"pending_reviews": results}, status=status.HTTP_200_OK)


class VendorProductReviewsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        if getattr(user, "rol", None) != "vendor":
            return Response(
                {'error': 'Solo los vendedores pueden consultar sus reseñas'},
                status=status.HTTP_403_FORBIDDEN
            )

        product_id = request.query_params.get("product_id")
        reviews = Review.objects.select_related("product", "user", "order_item").filter(
            product__vendor=user
        )
        if product_id:
            reviews = reviews.filter(product_id=product_id)

        data = []
        for review in reviews.order_by("-date_created")[:100]:
            data.append({
                "id": str(review.id),
                "product_id": str(review.product.id),
                "product_name": review.product.name,
                "rating": float(review.rating),
                "comment": review.comment,
                "date_created": review.date_created,
                "customer_name": review.user.full_name if hasattr(review.user, "full_name") else review.user.first_name,
                "transaction_id": str(review.order_item.order.transaction_id) if review.order_item else None,
                "extra_feedback": _format_extras(review.extra_feedback),
            })

        return Response({"reviews": data}, status=status.HTTP_200_OK)
