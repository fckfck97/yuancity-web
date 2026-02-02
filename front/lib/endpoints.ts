// Endpoints para la API
export const ENDPOINTS = {
  // Orders
  ORDERS_VENDOR: '/orders/vendor/orders',
  ORDERS_DETAIL: (transactionId: string) => `/orders/order/${transactionId}`,
  ORDERS_STATUS: (orderId: string) => `/orders/vendor/orders/${orderId}/status/`,
  ORDERS_CHAT: (transactionId: string) => `/orders/order-chat/${transactionId}/`,

  // Reviews
  REVIEWS_VENDOR: '/reviews/vendor',

  // Products
  PRODUCTS_LIST: '/products/',
  PRODUCTS_DETAIL: (productId: string) => `/products/${productId}/update/`,
  PRODUCTS_CREATE: '/products/',

  // Categories
  CATEGORIES_LIST: '/category/categories/list/',

  // Auth
  LOGIN_OTP_REQUEST: '/login/otp/request/web/',
  LOGIN_OTP_VERIFY: '/login/otp/verify/',
} as const;
