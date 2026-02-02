import React from "react";
import {
  X,
  User,
  CreditCard,
  ShoppingBag,
  Calendar,
  Mail,
  Phone,
  ExternalLink,
} from "lucide-react";

interface VendorDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  vendor: any;
  loading: boolean;
}

export default function VendorDetailsModal({
  isOpen,
  onClose,
  vendor,
  loading,
}: VendorDetailsModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      <div className="relative bg-white rounded-[2rem] w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 rounded-full bg-secondary/10 hover:bg-secondary/20 transition-colors"
        >
          <X size={20} />
        </button>

        {loading || !vendor ? (
          <div className="p-12 flex flex-col items-center justify-center space-y-4">
            <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            <p className="text-sm font-medium text-muted-foreground">
              Cargando información del vendedor...
            </p>
          </div>
        ) : (
          <div className="p-8 sm:p-10 space-y-8">
            {/* Header */}
            <div className="flex items-start gap-6">
              <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
                <User size={32} />
              </div>
              <div>
                <h2 className="text-2xl font-black text-foreground tracking-tight">
                  {vendor.full_name || "Vendedor Sin Nombre"}
                </h2>
                <div className="flex flex-wrap gap-4 mt-2 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1.5">
                    <Mail size={14} />
                    {vendor.email}
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Phone size={14} />
                    {vendor.phone}
                  </div>
                </div>
                <div className="mt-2 text-xs font-bold uppercase tracking-wider text-primary">
                  Miembro desde{" "}
                  {new Date(vendor.joined_at).toLocaleDateString()}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Stats */}
              <div className="bg-secondary/5 rounded-[1.5rem] p-6 space-y-4 border border-border/5">
                <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
                  <ShoppingBag size={16} /> Resumen de Ventas
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white p-4 rounded-xl shadow-soft-sm">
                    <div className="text-2xl font-black text-foreground">
                      {vendor.products_count}
                    </div>
                    <div className="text-[10px] font-bold text-muted-foreground uppercase">
                      Productos
                    </div>
                  </div>
                  <div className="bg-white p-4 rounded-xl shadow-soft-sm">
                    <div className="text-2xl font-black text-primary">
                      {vendor.total_items_sold}
                    </div>
                    <div className="text-[10px] font-bold text-muted-foreground uppercase">
                      Items Vendidos
                    </div>
                  </div>
                  <div className="col-span-2 bg-white p-4 rounded-xl shadow-soft-sm border-l-4 border-primary">
                    <div className="text-3xl font-black text-foreground">
                      $
                      {parseFloat(
                        vendor.total_sales_amount || "0",
                      ).toLocaleString("es-CO")}
                    </div>
                    <div className="text-[10px] font-bold text-muted-foreground uppercase">
                      Total Ganancias (Neto)
                    </div>
                  </div>
                </div>
              </div>

              {/* Bank Info */}
              <div className="bg-secondary/5 rounded-[1.5rem] p-6 space-y-4 border border-border/5">
                <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
                  <CreditCard size={16} /> Datos Bancarios
                </h3>
                {vendor.bank_account ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-white rounded-xl border border-border/10">
                      <div className="text-xs text-muted-foreground uppercase mb-1">
                        Banco
                      </div>
                      <div className="font-bold text-foreground">
                        {vendor.bank_account.bank_name}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-white rounded-xl border border-border/10">
                        <div className="text-xs text-muted-foreground uppercase mb-1">
                          Tipo de Cuenta
                        </div>
                        <div className="font-bold text-foreground">
                          {vendor.bank_account.account_type}
                        </div>
                      </div>
                      <div className="p-4 bg-white rounded-xl border border-border/10">
                        <div className="text-xs text-muted-foreground uppercase mb-1">
                          Número
                        </div>
                        <div className="font-mono font-bold text-foreground">
                          {vendor.bank_account.account_number}
                        </div>
                      </div>
                    </div>
                    <div className="p-4 bg-white rounded-xl border border-border/10">
                      <div className="text-xs text-muted-foreground uppercase mb-1">
                        Titular
                      </div>
                      <div className="font-bold text-foreground">
                        {vendor.bank_account.account_holder_name}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {vendor.bank_account.document_type}:{" "}
                        {vendor.bank_account.document_number}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-48 text-muted-foreground bg-white rounded-xl border border-dashed border-border/20">
                    <CreditCard size={32} className="mb-2 opacity-50" />
                    <p className="text-sm font-medium">Sin cuenta registrada</p>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Orders */}
            <div className="space-y-4">
              <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                <Calendar size={16} /> Órdenes Recientes
              </h3>
              <div className="overflow-hidden rounded-2xl border border-border/10">
                <table className="w-full text-sm">
                  <thead className="bg-secondary/10 text-muted-foreground font-bold uppercase text-xs">
                    <tr>
                      <th className="px-4 py-3 text-left">Orden</th>
                      <th className="px-4 py-3 text-left">Producto</th>
                      <th className="px-4 py-3 text-left">Estado</th>
                      <th className="px-4 py-3 text-right">Ganancia</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/10 bg-white">
                    {vendor.recent_orders && vendor.recent_orders.length > 0 ? (
                      vendor.recent_orders.map((order: any, i: number) => (
                        <tr key={i} className="hover:bg-secondary/5">
                          <td className="px-4 py-3 font-mono text-xs">
                            {order.transaction_id.substring(0, 8)}...
                            <div className="text-[10px] text-muted-foreground">
                              {new Date(order.date).toLocaleDateString()}
                            </div>
                          </td>
                          <td className="px-4 py-3 font-medium">
                            {order.product_name}
                          </td>
                          <td className="px-4 py-3">
                            <span
                              className={`inline-flex px-2 py-1 rounded-lg text-[10px] font-bold uppercase ${
                                order.status === "delivered"
                                  ? "bg-green-100 text-green-700"
                                  : order.status === "cancelled"
                                    ? "bg-red-100 text-red-700"
                                    : "bg-blue-100 text-blue-700"
                              }`}
                            >
                              {order.status}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right font-bold text-foreground">
                            ${parseFloat(order.amount).toLocaleString("es-CO")}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td
                          colSpan={4}
                          className="px-4 py-8 text-center text-muted-foreground italic"
                        >
                          No hay ventas recientes
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
