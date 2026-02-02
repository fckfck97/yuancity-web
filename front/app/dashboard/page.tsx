"use client";

import React, { useEffect, useState } from "react";
import {
  BadgeCheck,
  MessageCircle,
  Package,
  ShoppingCart,
  Users,
} from "lucide-react";
import { buildApiUrl, fetchWithAuth, loadAuth, loadUser } from "@/lib/auth";
import { useRouter } from "next/navigation";
import SummaryView from "./views/SummaryView";
import ProductsView from "./views/ProductsView";
import OrdersView from "./views/OrdersView";
import SupportView from "./views/SupportView";
import ReviewsView from "./views/ReviewsView";
import OrderDetailsModal from "./views/OrderDetailsModal";
import ProductModal from "./views/ProductModal";
import { useDashboard } from "./DashboardContext";
import StatCard from "./components/StatCard";

const DEFAULT_SALES_SERIES = [
  { month: "Ene", sales: 0, clients: 0 },
  { month: "Feb", sales: 0, clients: 0 },
  { month: "Mar", sales: 0, clients: 0 },
  { month: "Abr", sales: 0, clients: 0 },
  { month: "May", sales: 0, clients: 0 },
  { month: "Jun", sales: 0, clients: 0 },
];

const DEFAULT_CATEGORY_DATA: Array<{
  name: string;
  value: number;
  color: string;
}> = [];

const CATEGORY_COLORS = [
  "#10b981",
  "#f59e0b",
  "#f97316",
  "#ef4444",
  "#6366f1",
  "#14b8a6",
];

const requestApi = async (path: string, options: RequestInit = {}) => {
  const res = await fetchWithAuth(buildApiUrl(path), options);
  let data = null;
  try {
    data = await res.json();
  } catch (error) {
    data = null;
  }
  return { ok: res.ok, data, status: res.status };
};

const dashboardApi = {
  getAdminSummary: () => requestApi("/payment/admin/dashboard/"),
  getOrders: () => requestApi("/payment/admin/orders/"),
  getOrderDetails: (transactionId: string) =>
    requestApi(`/payment/admin/orders/${transactionId}/`),
  updateOrderStatus: (orderId: string, status: string) =>
    requestApi(`/payment/admin/orders/${orderId}/status/`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
  getProducts: () => requestApi("/payment/admin/products/"),
  getReviews: () => requestApi("/payment/admin/reviews/"),
  getCategories: () => requestApi("/category/categories/list/"),
  getChatMessages: (transactionId: string) =>
    requestApi(`/orders/chat/${transactionId}/`),
  sendChatMessage: (transactionId: string, message: string) =>
    requestApi(`/orders/chat/${transactionId}/`, {
      method: "POST",
      body: JSON.stringify({ text: message }),
    }),
  saveProduct: (formData: FormData, productId?: string) =>
    requestApi(
      productId ? `/products/${productId}/update/` : "/products/",
      {
        method: productId ? "PUT" : "POST",
        body: formData,
      },
    ),
  deleteProduct: (productId: string) =>
    requestApi(`/products/${productId}/update/`, {
      method: "PATCH",
      body: JSON.stringify({ is_available: false }),
    }),
};

const normalizeChatMessage = (message: any, isLocalSender = false) => {
  return {
    ...message,
    message: message.message ?? message.text ?? "",
    sender_role: message.sender_role || (isLocalSender ? "vendor" : "buyer"),
  };
};

export default function CrediMuebleDashboard() {
  const router = useRouter();
  const { activeView, createProductRequest } = useDashboard();

  const [loading, setLoading] = useState(true);
  const [orders, setOrders] = useState<any[]>([]);
  const [reviews, setReviews] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [user, setUser] = useState<any>(null);
  const [selectedOrderDetails, setSelectedOrderDetails] = useState<any>(null);
  const [selectedOrderChat, setSelectedOrderChat] = useState<any>(null);
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isAddProductModalOpen, setIsAddProductModalOpen] = useState(false);
  const [newProduct, setNewProduct] = useState({
    id: "",
    name: "",
    category: "",
    price: "",
    stock: "",
    description: "",
    images: [] as any[],
  });
  const [selectedImageFiles, setSelectedImageFiles] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [dbCategories, setDbCategories] = useState<any[]>([]);
  const [isEditMode, setIsEditMode] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [summaryData, setSummaryData] = useState({
    totalSales: 0,
    totalClients: 0,
    totalStock: 0,
    avgPrice: 0,
  });
  const [salesSeries, setSalesSeries] = useState(DEFAULT_SALES_SERIES);
  const [categoryData, setCategoryData] = useState(DEFAULT_CATEGORY_DATA);
  const [adminStats, setAdminStats] = useState({
    ordersTotal: 0,
    usersTotal: 0,
    vendorsWithProducts: 0,
    vendorsWithSales: 0,
    supportUnread: 0,
  });

  useEffect(() => {
    const auth = loadAuth();
    if (!auth?.access) {
      router.replace("/login");
      return;
    }

    const userData = loadUser();
    setUser(userData);

    const loadDashboardData = async () => {
      setLoading(true);
      try {
        const [
          summaryRes,
          ordersRes,
          reviewsRes,
          productsRes,
          categoriesRes,
        ] = await Promise.all([
          dashboardApi.getAdminSummary(),
          dashboardApi.getOrders(),
          dashboardApi.getReviews(),
          dashboardApi.getProducts(),
          dashboardApi.getCategories(),
        ]);

        const hasSummary = summaryRes.ok && summaryRes.data;
        if (hasSummary) {
          const stats = summaryRes.data.stats || {};
          setSummaryData({
            totalSales: Number(stats.sales_total || 0),
            totalClients: Number(stats.users_total || 0),
            totalStock: Number(stats.products_total || 0),
            avgPrice: Number(stats.avg_order_value || 0),
          });
          setAdminStats({
            ordersTotal: Number(stats.orders_total || 0),
            usersTotal: Number(stats.users_total || 0),
            vendorsWithProducts: Number(stats.vendors_with_products || 0),
            vendorsWithSales: Number(stats.vendors_with_sales || 0),
            supportUnread: Number(stats.support_unread || 0),
          });

          if (Array.isArray(summaryRes.data.sales_series)) {
            setSalesSeries(
              summaryRes.data.sales_series.map((item: any) => ({
                month: item.month,
                sales: Number(item.sales || 0),
                clients: Number(item.clients || 0),
              })),
            );
          }

          if (Array.isArray(summaryRes.data.category_breakdown)) {
            setCategoryData(
              summaryRes.data.category_breakdown.map((item: any, idx: number) => ({
                name: item.name,
                value: Number(item.value || 0),
                color: CATEGORY_COLORS[idx % CATEGORY_COLORS.length],
              })),
            );
          }
        }

        if (ordersRes.ok && ordersRes.data) {
          const fetchedOrders = ordersRes.data.orders || [];
          setOrders(fetchedOrders);

          if (!hasSummary) {
            const totalSalesValue = fetchedOrders.reduce(
              (acc: number, o: any) => acc + parseFloat(o.order_total || 0),
              0,
            );
            const totalClientsSet = new Set(
              fetchedOrders.map((o: any) => o.customer_email),
            );

            setSummaryData((prev) => ({
              ...prev,
              totalSales: totalSalesValue,
              totalClients: totalClientsSet.size,
            }));
            setAdminStats((prev) => ({
              ...prev,
              ordersTotal: fetchedOrders.length,
              usersTotal: totalClientsSet.size,
            }));
          }
        }

        if (reviewsRes.ok && reviewsRes.data) {
          setReviews(
            reviewsRes.data.results || reviewsRes.data.reviews || [],
          );
        }

        if (productsRes.ok && productsRes.data) {
          const fetchedProducts = productsRes.data.results || productsRes.data;
          if (Array.isArray(fetchedProducts)) {
            setProducts(fetchedProducts);
            if (!hasSummary) {
              const totalStockValue = fetchedProducts.reduce(
                (acc: number, p: any) => acc + Number(p.stock || 0),
                0,
              );
              const avgPriceValue =
                fetchedProducts.length > 0
                  ? fetchedProducts.reduce(
                      (acc: number, p: any) => acc + parseFloat(p.price || 0),
                      0,
                    ) / fetchedProducts.length
                  : 0;

              setSummaryData((prev) => ({
                ...prev,
                totalStock: totalStockValue,
                avgPrice: avgPriceValue,
              }));
            }
          }
        }

        if (categoriesRes.ok && categoriesRes.data) {
          setDbCategories(categoriesRes.data.results || []);
        }
      } catch (error) {
        console.error("Error loading dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [router]);

  useEffect(() => {
    if (createProductRequest > 0) {
      resetForm();
      setIsAddProductModalOpen(true);
    }
  }, [createProductRequest]);

  const fetchOrderDetails = async (transactionId: string) => {
    try {
      const res = await dashboardApi.getOrderDetails(transactionId);
      if (res.ok && res.data) {
        setSelectedOrderDetails(res.data.order);
      }
    } catch (error) {
      console.error("Error fetching order details:", error);
    }
  };

  const fetchChatMessages = async (transactionId: string) => {
    try {
      const res = await dashboardApi.getChatMessages(transactionId);
      if (res.ok && res.data) {
        const messages = res.data.messages || [];
        setChatMessages(messages.map((msg: any) => normalizeChatMessage(msg)));
      }
    } catch (error) {
      console.error("Error fetching chat messages:", error);
    }
  };

  const sendChatMessage = async () => {
    if (!selectedOrderChat || !newMessage.trim()) return;
    try {
      const res = await dashboardApi.sendChatMessage(
        selectedOrderChat.transaction_id,
        newMessage.trim(),
      );
      if (res.ok && res.data) {
        setChatMessages((prev: any) => [
          ...prev,
          normalizeChatMessage(res.data, true),
        ]);
        setNewMessage("");
      }
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const updateOrderStatus = async (orderId: string, newStatus: string) => {
    try {
      const res = await dashboardApi.updateOrderStatus(orderId, newStatus);
      if (res.ok) {
        setOrders((prev: any) =>
          prev.map((o: any) =>
            o.order_id === orderId ? { ...o, status: newStatus } : o,
          ),
        );
      }
    } catch (error) {
      console.error("Error updating order status:", error);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setSelectedImageFiles((prev) => [...prev, ...files]);

      const newPreviews = files.map((file) => URL.createObjectURL(file));
      setImagePreviews((prev) => [...prev, ...newPreviews]);
    }
  };

  const removeImagePreview = (index: number) => {
    setImagePreviews((prev) => prev.filter((_, i) => i !== index));
    setSelectedImageFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const resetForm = () => {
    setNewProduct({
      id: "",
      name: "",
      category: "",
      price: "",
      stock: "",
      description: "",
      images: [],
    });
    setSelectedImageFiles([]);
    setImagePreviews([]);
    setIsEditMode(false);
  };

  const handleEditProduct = (product: any) => {
    setNewProduct({
      id: product.id,
      name: product.name,
      category: product.category_detail?.id || "",
      price: product.price,
      stock: product.stock,
      description: product.description || "",
      images: product.images || [],
    });
    setImagePreviews([]);
    setSelectedImageFiles([]);
    setIsEditMode(true);
    setIsAddProductModalOpen(true);
  };

  const handleDeleteProduct = async (productId: string) => {
    if (!confirm("¿Estás seguro de que deseas eliminar este producto?")) return;
    setIsDeleting(true);
    try {
      const res = await dashboardApi.deleteProduct(productId);
      if (res.ok) {
        setProducts((prev) => prev.filter((p) => p.id !== productId));
      }
    } catch (error) {
      console.error("Error deleting product:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleSaveProduct = async () => {
    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("name", newProduct.name);
      formData.append("price", newProduct.price);
      formData.append("stock", newProduct.stock);
      formData.append("description", newProduct.description);
      if (newProduct.category) {
        formData.append("categories", newProduct.category);
      }

      selectedImageFiles.forEach((file, index) => {
        formData.append(`media_${index}`, file);
        formData.append(`media_${index}_order`, index.toString());
      });

      if (selectedImageFiles.length > 0) {
        formData.append("media_count", selectedImageFiles.length.toString());
      }

      const res = await dashboardApi.saveProduct(
        formData,
        isEditMode ? newProduct.id : undefined,
      );

      if (res.ok) {
        const productsRes = await dashboardApi.getProducts();
        if (productsRes.ok && productsRes.data) {
          setProducts(productsRes.data.results || productsRes.data);
        }
        setIsAddProductModalOpen(false);
        resetForm();
      } else {
        console.error("Error saving product:", res.data);
        alert("Error al guardar el producto: " + JSON.stringify(res.data));
      }
    } catch (error) {
      console.error("Error saving product:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
        <p className="text-muted-foreground font-medium animate-pulse">
          Cargando tu panel...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white p-6 sm:p-8 rounded-[2rem] border border-border/10 shadow-soft-xl">
        <div className="space-y-1">
          <h1 className="text-3xl font-black text-foreground tracking-tight uppercase">
            Panel de Control
          </h1>
          <p className="text-muted-foreground font-medium">
            Gestiona tu tienda y revisa tus estadísticas en tiempo real.
          </p>
        </div>

      </header>

      <main className="animate-in fade-in duration-500">
        {activeView === "summary" && (
          <div className="space-y-10">
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-6">
              <StatCard
                title="Compras"
                value={adminStats.ordersTotal.toLocaleString()}
                icon={<ShoppingCart />}
                trend="Actual"
                trendUp
              />
              <StatCard
                title="Registrados"
                value={adminStats.usersTotal.toLocaleString()}
                icon={<Users />}
                trend="Actual"
                trendUp
              />
              <StatCard
                title="Publicaron Productos"
                value={adminStats.vendorsWithProducts.toLocaleString()}
                icon={<Package />}
                trend="Actual"
                trendUp
              />
              <StatCard
                title="Vendieron"
                value={adminStats.vendorsWithSales.toLocaleString()}
                icon={<BadgeCheck />}
                trend="Actual"
                trendUp
              />
              <StatCard
                title="Soporte Pendiente"
                value={adminStats.supportUnread.toLocaleString()}
                icon={<MessageCircle />}
                trend="Actual"
                trendUp
              />
            </div>

            <SummaryView
              summaryData={summaryData}
              salesData={
                salesSeries.length > 0 ? salesSeries : DEFAULT_SALES_SERIES
              }
              categoryData={
                categoryData.length > 0 ? categoryData : DEFAULT_CATEGORY_DATA
              }
            />
          </div>
        )}

        {activeView === "products" && (
          <ProductsView
            products={products}
            isDeleting={isDeleting}
            onCreate={() => setIsAddProductModalOpen(true)}
            onEdit={handleEditProduct}
            onDelete={handleDeleteProduct}
          />
        )}

        {activeView === "orders" && (
          <OrdersView
            orders={orders}
            onUpdateStatus={updateOrderStatus}
            onOpenDetails={fetchOrderDetails}
          />
        )}

        {activeView === "support" && (
          <SupportView
            orders={orders}
            selectedOrderChat={selectedOrderChat}
            chatMessages={chatMessages}
            newMessage={newMessage}
            onSelectChat={(order) => {
              setSelectedOrderChat(order);
              setChatMessages([]);
              fetchChatMessages(order.transaction_id);
            }}
            onMessageChange={setNewMessage}
            onSendMessage={sendChatMessage}
          />
        )}

        {activeView === "reviews" && <ReviewsView reviews={reviews} />}
      </main>

      <OrderDetailsModal
        order={selectedOrderDetails}
        onClose={() => setSelectedOrderDetails(null)}
      />

      <ProductModal
        isOpen={isAddProductModalOpen}
        isEditMode={isEditMode}
        isSubmitting={isSubmitting}
        newProduct={newProduct}
        dbCategories={dbCategories}
        imagePreviews={imagePreviews}
        onClose={() => {
          setIsAddProductModalOpen(false);
          resetForm();
        }}
        onFieldChange={(field, value) =>
          setNewProduct((prev) => ({ ...prev, [field]: value }))
        }
        onImageChange={handleImageChange}
        onRemovePreview={removeImagePreview}
        onSave={handleSaveProduct}
      />
    </div>
  );
}
