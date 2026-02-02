import React from "react";
import { Search, ShoppingCart, ArrowUpRight } from "lucide-react";
import StatusBadge from "../components/StatusBadge";

interface OrdersViewProps {
  orders: any[];
  onUpdateStatus: (orderId: string, status: string) => void;
  onOpenDetails: (transactionId: string) => void;
}

export default function OrdersView({
  orders,
  onUpdateStatus,
  onOpenDetails,
}: OrdersViewProps) {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 sm:p-8 rounded-[2.5rem] border border-border/10 shadow-soft-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <h2 className="text-2xl font-bold text-foreground">
            Órdenes de compra
          </h2>
          <div className="relative w-full sm:w-72">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              size={18}
            />
            <input
              type="text"
              placeholder="Buscar compra..."
              className="w-full h-11 pl-10 pr-4 bg-secondary/30 rounded-xl border-none outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
            />
          </div>
        </div>

        {orders.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
            <div className="w-20 h-20 bg-secondary/30 rounded-full flex items-center justify-center text-muted-foreground">
              <ShoppingCart size={40} />
            </div>
            <div className="space-y-1">
              <h3 className="text-xl font-bold">
                No hay compras recientes
              </h3>
              <p className="text-muted-foreground">
                Cuando se registren nuevas compras, aparecerán aquí.
              </p>
            </div>
          </div>
        ) : (
          <>
            <div className="grid gap-4 md:hidden">
              {orders.map((order: any) => (
                <div
                  key={order.order_id}
                  className="bg-secondary/10 rounded-[1.5rem] p-5 border border-border/5 space-y-4"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-bold text-foreground">
                        #{order.transaction_id.slice(0, 8)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(order.date_issued).toLocaleDateString("es-ES", {
                          day: "2-digit",
                          month: "short",
                        })}
                      </p>
                    </div>
                    <StatusBadge status={order.status} />
                  </div>
                  <div className="text-sm text-foreground font-semibold">
                    {order.customer_name}
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs text-muted-foreground">Total</p>
                      <p className="font-black">
                        ${parseFloat(order.order_total).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <select
                        className="text-xs font-bold bg-white border border-border/20 rounded-lg px-2 py-1 outline-none"
                        value={order.status}
                        onChange={(e) =>
                          onUpdateStatus(order.order_id, e.target.value)
                        }
                      >
                        <option value="not_processed">Pendiente</option>
                        <option value="processed">Procesado</option>
                        <option value="shipping">Enviado</option>
                        <option value="delivered">Entregado</option>
                        <option value="cancelled">Cancelado</option>
                      </select>
                      <button
                        onClick={() => onOpenDetails(order.transaction_id)}
                        className="p-2 bg-white text-primary rounded-xl shadow-soft-sm hover:shadow-soft-md transition-all border border-border/5"
                      >
                        <ArrowUpRight size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="hidden md:block overflow-x-auto">
              <table className="w-full border-separate border-spacing-y-4">
                <thead>
                  <tr className="text-left text-muted-foreground text-xs font-bold uppercase tracking-widest">
                    <th className="px-6 pb-2">ID / Fecha</th>
                    <th className="px-6 pb-2">Cliente</th>
                    <th className="px-6 pb-2">Total</th>
                    <th className="px-6 pb-2">Estado</th>
                    <th className="px-6 pb-2">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order: any) => (
                    <tr
                      key={order.order_id}
                      className="bg-secondary/10 hover:bg-secondary/20 transition-all group"
                    >
                      <td className="px-6 py-5 rounded-l-[1.5rem]">
                        <div className="font-bold text-sm text-foreground">
                          #{order.transaction_id.slice(0, 8)}
                        </div>
                        <div className="text-[10px] text-muted-foreground font-medium uppercase tracking-tighter">
                          {new Date(order.date_issued).toLocaleDateString("es-ES", {
                            day: "2-digit",
                            month: "short",
                          })}
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <div className="font-bold text-sm text-foreground">
                          {order.customer_name}
                        </div>
                        <div className="text-[10px] text-muted-foreground lowercase">
                          {order.customer_email}
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <div className="font-black text-sm text-foreground">
                          ${parseFloat(order.order_total).toLocaleString()}
                        </div>
                        <div className="text-[10px] text-muted-foreground uppercase">
                          {order.items_count} ítems
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <StatusBadge status={order.status} />
                      </td>
                      <td className="px-6 py-5 rounded-r-[1.5rem]">
                        <div className="flex items-center gap-2">
                          <select
                            className="text-xs font-bold bg-white border border-border/20 rounded-lg px-2 py-1 outline-none focus:ring-2 focus:ring-primary/20"
                            value={order.status}
                            onChange={(e) =>
                              onUpdateStatus(order.order_id, e.target.value)
                            }
                          >
                            <option value="not_processed">Pendiente</option>
                            <option value="processed">Procesado</option>
                            <option value="shipping">Enviado</option>
                            <option value="delivered">Entregado</option>
                            <option value="cancelled">Cancelado</option>
                          </select>
                          <button
                            onClick={() => onOpenDetails(order.transaction_id)}
                            className="p-2 bg-white text-primary rounded-xl shadow-soft-sm hover:shadow-soft-md transition-all border border-border/5"
                          >
                            <ArrowUpRight size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
