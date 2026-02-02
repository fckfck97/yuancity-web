import React from "react";
import { Package, Edit, Trash2 } from "lucide-react";

interface ProductsViewProps {
  products: any[];
  isDeleting: boolean;
  onCreate: () => void;
  onEdit: (product: any) => void;
  onDelete: (productId: string) => void;
}

const getProductImage = (product: any) => {
  if (product.first_image) return product.first_image;
  const image = product.images?.[0]?.image;
  return image || "";
};

const getCategoryLabel = (product: any) => {
  return (
    product.category_detail?.name ||
    product.categories_detail?.[0]?.name ||
    "Mueble"
  );
};

export default function ProductsView({
  products,
  isDeleting,
  onCreate,
  onEdit,
  onDelete,
}: ProductsViewProps) {
  return (
    <div className="space-y-8">
      <div className="bg-white p-6 sm:p-8 rounded-[2.5rem] border border-border/10 shadow-soft-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-8">
          <div>
            <h2 className="text-2xl font-black text-foreground uppercase tracking-tight">
              Gestión del Catálogo
            </h2>
            <p className="text-muted-foreground font-medium">
              Carga nuevos muebles y actualiza existencias.
            </p>
          </div>
          <button
            className="bg-primary text-primary-foreground px-6 sm:px-8 py-3 sm:py-4 rounded-2xl shadow-soft-lg hover:shadow-soft-xl hover:scale-105 transition-all font-black uppercase tracking-widest flex items-center gap-3"
            onClick={onCreate}
          >
            <Package size={20} />
            NUEVO PRODUCTO
          </button>
        </div>

        {products.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 bg-secondary/10 rounded-[2rem] border-2 border-dashed border-border/20 text-center">
            <Package size={48} className="text-muted-foreground opacity-20 mb-4" />
            <p className="font-bold text-muted-foreground">
              Tu catálogo está vacío
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
            {products.map((product: any) => {
              const image = getProductImage(product);
              const categoryLabel = getCategoryLabel(product);
              return (
                <div
                  key={product.id}
                  className="bg-white p-4 rounded-[2rem] border border-border/10 shadow-soft-md hover:shadow-soft-lg transition-all space-y-4"
                >
                  <div className="aspect-square rounded-2xl bg-secondary/20 overflow-hidden relative">
                    {image ? (
                      <img
                        src={image}
                        alt={product.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                        <Package size={48} className="opacity-10" />
                      </div>
                    )}
                    <div className="absolute top-4 right-4 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-lg text-[10px] font-black uppercase shadow-soft-sm">
                      {categoryLabel}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-bold text-foreground truncate">
                      {product.name}
                    </h3>
                    <p className="text-[10px] text-muted-foreground font-black uppercase tracking-widest">
                      Stock: {product.stock ?? 0} unidades
                    </p>
                  </div>
                  <div className="flex items-center justify-between pt-2">
                    <span className="font-black text-primary text-xl tracking-tighter">
                      ${parseFloat(product.price || 0).toLocaleString()}
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => onEdit(product)}
                        className="p-2 bg-secondary/30 rounded-xl text-foreground hover:bg-secondary/50 transition-colors"
                      >
                        <Edit size={16} />
                      </button>
                      <button
                        onClick={() => onDelete(product.id)}
                        disabled={isDeleting}
                        className="p-2 bg-red-50 rounded-xl text-red-500 hover:bg-red-100 transition-colors"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
