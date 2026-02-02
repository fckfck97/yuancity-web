import React from "react";
import { Users, CreditCard, Search } from "lucide-react";
import { Users, ShoppingBag } from "lucide-react";

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
                    Acciones
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
