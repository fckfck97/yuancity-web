import React from "react";
import { Users, ShoppingBag, CreditCard, Search } from "lucide-react";

interface VendorsViewProps {
  vendors: any[];
  onOpenDetails: (userId: string) => void;
}

export default function VendorsView({
  vendors,
  onOpenDetails,
}: VendorsViewProps) {
  return (
    <div className="space-y-8">
      <div className="bg-white p-6 sm:p-8 rounded-[2.5rem] border border-border/10 shadow-soft-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-8">
          <div>
            <h2 className="text-2xl font-black text-foreground uppercase tracking-tight">
              Gestión de Usuarios
            </h2>
            <p className="text-muted-foreground font-medium">
              Administra vendedores y clientes registrados.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-secondary/10 px-4 py-2 rounded-full">
            <Users size={20} className="text-primary" />
            <span className="font-bold text-foreground">
              {vendors.length} Usuarios
            </span>
          </div>
        </div>

        <div className="overflow-hidden rounded-[2rem] border border-border/10">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-secondary/5 border-b border-border/10">
                  <th className="text-left py-4 px-6 font-black text-xs uppercase tracking-widest text-muted-foreground">
                    Usuario
                  </th>
                  <th className="text-left py-4 px-6 font-black text-xs uppercase tracking-widest text-muted-foreground">
                    Rol
                  </th>
                  <th className="text-left py-4 px-6 font-black text-xs uppercase tracking-widest text-muted-foreground">
                    Productos
                  </th>
                  <th className="text-left py-4 px-6 font-black text-xs uppercase tracking-widest text-muted-foreground">
                    Fecha Registro
                  </th>
                  <th className="text-right py-4 px-6 font-black text-xs uppercase tracking-widest text-muted-foreground">
                    Cuenta Bancaria
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/10">
                {vendors.map((vendor: any) => {
                  const isVendor = vendor.products_count > 0;
                  return (
                    <tr
                      key={vendor.user_id}
                      className="group hover:bg-secondary/5 transition-colors cursor-pointer"
                      onClick={() => onOpenDetails(vendor.user_id)}
                    >
                      <td className="py-4 px-6">
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-gray-500 font-bold uppercase">
                            {vendor.full_name?.charAt(0) ||
                              vendor.email?.charAt(0)}
                          </div>
                          <div>
                            <p className="font-bold text-foreground">
                              {vendor.full_name || "Sin Nombre"}
                            </p>
                            <p className="text-xs text-muted-foreground font-medium">
                              {vendor.email}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        {isVendor ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-primary/10 text-primary uppercase tracking-wide">
                            Vendedor
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-secondary/20 text-muted-foreground uppercase tracking-wide">
                            Cliente
                          </span>
                        )}
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center gap-2">
                          <ShoppingBag
                            size={16}
                            className={
                              isVendor
                                ? "text-primary"
                                : "text-muted-foreground/50"
                            }
                          />
                          <span
                            className={`font-bold ${isVendor ? "text-foreground" : "text-muted-foreground"}`}
                          >
                            {vendor.products_count}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <span className="text-sm font-medium text-muted-foreground">
                          {vendor.joined_at
                            ? new Date(vendor.joined_at).toLocaleDateString()
                            : "N/A"}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-right">
                        {vendor.bank_account ? (
                          <div className="flex items-center justify-end gap-2 text-primary">
                            <CreditCard size={16} />
                            <span className="text-xs font-bold uppercase">
                              {vendor.bank_account.bank_name}
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground italic">
                            No registrada
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
