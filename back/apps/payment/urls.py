from django.urls import path

from .views import (
    CheckoutSummaryView,
    StripeIntentView,
    CheckoutCompleteView,
    PaymentSheetView,
    VendorBankAccountView,
    VendorPayoutSummaryView,
    VendorPayoutWithdrawView,
    FinancePortalLoginView,
    FinanceDashboardSummaryView,
    FinanceOrderListView,
    FinanceOrderDetailView,
    FinancePayoutListView,
    FinancePayoutStatusUpdateView,
    AdminDashboardOrdersView,
    AdminDashboardOrderDetailView,
    AdminDashboardOrderStatusView,
    AdminDashboardProductsView,
    AdminDashboardReviewsView,
)

app_name = "payment"

urlpatterns = [

    # Nuevos endpoints de Stripe Checkout
    path('checkout/summary/', CheckoutSummaryView.as_view(), name='checkout_summary'),
    path('checkout/payment-sheet/', PaymentSheetView.as_view(), name='payment_sheet'),
    path('checkout/stripe-intent/', StripeIntentView.as_view(), name='stripe_intent'),
    path('checkout/complete/', CheckoutCompleteView.as_view(), name='checkout_complete'),
    path('wallet/bank-account/', VendorBankAccountView.as_view(), name='wallet_bank_account'),
    path('wallet/summary/', VendorPayoutSummaryView.as_view(), name='wallet_summary'),
    path('wallet/payouts/<uuid:pk>/withdraw/', VendorPayoutWithdrawView.as_view(), name='wallet_payout_withdraw'),
    path('finance/login/', FinancePortalLoginView.as_view(), name='finance_login'),
    path('finance/dashboard/', FinanceDashboardSummaryView.as_view(), name='finance_dashboard'),
    path('finance/orders/', FinanceOrderListView.as_view(), name='finance_orders'),
    path('finance/orders/<uuid:pk>/', FinanceOrderDetailView.as_view(), name='finance_order_detail'),
    path('finance/payouts/', FinancePayoutListView.as_view(), name='finance_payouts'),
    path('finance/payouts/<uuid:pk>/status/', FinancePayoutStatusUpdateView.as_view(), name='finance_payout_status'),
    path('admin/dashboard/', FinanceDashboardSummaryView.as_view(), name='admin_dashboard'),
    path('admin/orders/', AdminDashboardOrdersView.as_view(), name='admin_orders'),
    path('admin/orders/<str:transaction_id>/', AdminDashboardOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin/orders/<uuid:pk>/status/', AdminDashboardOrderStatusView.as_view(), name='admin_order_status'),
    path('admin/products/', AdminDashboardProductsView.as_view(), name='admin_products'),
    path('admin/reviews/', AdminDashboardReviewsView.as_view(), name='admin_reviews'),
]
