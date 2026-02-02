import React from "react";
import { Users, CreditCard, Search } from "lucide-react";

interface VendorsViewProps {
  vendors: any[];
  onOpenDetails: (userId: string) => void;
}

export default function VendorsView({
  vendors,
  onOpenDetails,
}: VendorsViewProps) {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 sm:p-8 rounded-[2.5rem] border border-border/10 shadow-soft-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <h2 className="text-2xl font-bold text-foreground">Vendedores</h2>
          <div className="relative w-full sm:w-72">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              size={18}
            />
            <input
              type="text"
              placeholder="Buscar vendedor..."
              className="w-full h-11 pl-10 pr-4 bg-secondary/30 rounded-xl border-none outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
            />
          </div>
        </div>

        {vendors.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
            <div className="w-20 h-20 bg-secondary/30 rounded-full flex items-center justify-center text-muted-foreground">
              <Users size={40} />
            </div>
            <div className="space-y-1">
              <h3 className="text-xl font-bold">
                No hay vendedores registrados
              </h3>
              <p className="text-muted-foreground">
                Los usuarios que publiquen productos aparecerán aquí.
              </p>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-separate border-spacing-y-4">
              <thead>
                <tr className="text-left text-muted-foreground text-xs font-bold uppercase tracking-widest">
                  <th className="px-6 pb-2">Vendedor</th>
                  <th className="px-6 pb-2">Contacto</th>
                  <th className="px-6 pb-2">Productos</th>
                  <th className="px-6 pb-2">Cuenta Bancaria</th>
                </tr>
              </thead>
              <tbody>
                {vendors.map((vendor: any) => (
                  <tr
                    key={vendor.user_id}
                    onClick={() => onOpenDetails(vendor.user_id)}
                    className="bg-secondary/10 hover:bg-secondary/20 transition-all group cursor-pointer"
                  >
                    <td className="px-6 py-5 rounded-l-[1.5rem]">
                      <div className="font-bold text-sm text-foreground">
                        {vendor.full_name || "Sin nombre"}
                      </div>
                      <div className="text-[10px] text-muted-foreground lowercase">
                        {vendor.email}
                      </div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="text-sm font-medium text-foreground">
                        {vendor.phone || "N/A"}
                      </div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="font-black text-lg text-primary">
                        {vendor.products_count}
                      </div>
                      <div className="text-[10px] text-muted-foreground uppercase">
                        Publicados
                      </div>
                    </td>
                    <td className="px-6 py-5 rounded-r-[1.5rem]">
                      {vendor.bank_account ? (
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <CreditCard size={14} className="text-primary" />
                            <span className="font-bold text-xs uppercase">
                              {vendor.bank_account.bank_name}
                            </span>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {vendor.bank_account.account_type} •{" "}
                            {vendor.bank_account.account_number}
                          </div>
                          <div className="text-[10px] text-muted-foreground">
                            {vendor.bank_account.document_type}:{" "}
                            {vendor.bank_account.document_number}
                          </div>
                          <div className="text-[10px] font-bold text-foreground">
                            {vendor.bank_account.account_holder_name}
                          </div>
                        </div>
                      ) : (
                        <div className="text-xs text-muted-foreground italic">
                          Sin cuenta registrada
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
