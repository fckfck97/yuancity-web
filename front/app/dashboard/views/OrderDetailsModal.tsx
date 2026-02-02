import React from "react";
import { Users, Package, Filter } from "lucide-react";
import StatusBadge from "../components/StatusBadge";

interface OrderDetailsModalProps {
  order: any | null;
  onClose: () => void;
}

export default function OrderDetailsModal({
  order,
  onClose,
}: OrderDetailsModalProps) {
  if (!order) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-foreground/20 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-white w-full max-w-2xl rounded-[2.5rem] shadow-soft-2xl overflow-hidden border border-border/10 flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-300">
        <div className="p-8 border-b border-border/5 flex justify-between items-center bg-secondary/5">
          <div>
            <h3 className="text-2xl font-black text-foreground uppercase tracking-tight">
              Detalles de la Compra
            </h3>
            <p className="text-sm text-muted-foreground font-medium">
              ID: #{order.transaction_id}
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-12 h-12 rounded-2xl bg-white flex items-center justify-center text-muted-foreground hover:text-foreground shadow-soft-sm transition-all border border-border/10"
          >
            <Filter size={20} className="rotate-45" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-8 space-y-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-primary">
              <Users size={18} />
              <h4 className="font-bold uppercase tracking-wider text-xs">
                Información del Cliente
              </h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-secondary/10 p-6 rounded-3xl border border-border/5">
              <div className="space-y-1">
                <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">
                  Nombre
                </p>
                <p className="font-bold text-foreground">{order.full_name}</p>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">
                  Teléfono
                </p>
                <p className="font-bold text-foreground">
                  {order.telephone_number}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">
                  Email
                </p>
                <p className="font-bold text-foreground">
                  {order.customer_email}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">
                  Dirección de Entrega
                </p>
                <p className="font-bold text-foreground text-sm">
                  {order.address_line_1}, {order.city}
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2 text-primary">
              <Package size={18} />
              <h4 className="font-bold uppercase tracking-wider text-xs">
                Productos
              </h4>
            </div>
            <div className="space-y-3">
              {order.items?.map((item: any, idx: number) => (
                <div
                  key={idx}
                  className="flex justify-between items-center p-4 bg-white border border-border/10 rounded-2xl"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-secondary/30 rounded-xl flex items-center justify-center text-primary font-bold">
                      {item.count}x
                    </div>
                    <div>
                      <p className="font-bold text-sm">{item.name}</p>
                      <p className="text-xs text-muted-foreground">
                        ${parseFloat(item.price).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <p className="font-black text-sm">
                    ${(item.count * parseFloat(item.price)).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-border/10 flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <StatusBadge status={order.status} />
                <span className="text-[10px] font-bold text-muted-foreground uppercase bg-secondary/30 px-2 py-1 rounded-lg">
                    {order.payment_method === "credit" ? "Crédito" : "Compra"}
                  </span>
              </div>
              <p className="text-[10px] text-muted-foreground font-medium">
                Fecha: {new Date(order.date_issued).toLocaleString()}
              </p>
            </div>
            <div className="text-right space-y-1">
              <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">
                Total a Pagar
              </p>
              <p className="text-3xl font-black text-primary tracking-tighter">
                ${parseFloat(order.amount).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
