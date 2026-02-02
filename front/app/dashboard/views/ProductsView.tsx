import React from "react";
import { Package, Edit, Trash2 } from "lucide-react";

interface ProductsViewProps {
  products: any[];
  currentUser: any;
  isDeleting: boolean;
  onCreate: () => void;
  onEdit: (product: any) => void;
  onDelete: (productId: string) => void;
}

// ... existing helper functions ...

export default function ProductsView({
  products,
  currentUser,
  isDeleting,
  onCreate,
  onEdit,
  onDelete,
}: ProductsViewProps) {
  // ... existing render ...
              const isOwner =
                currentUser?.id &&
                (product.vendor === currentUser.id ||
                  product.vendor?.id === currentUser.id);

              return (
                <div
                  key={product.id}
                  className="bg-white p-4 rounded-[2rem] border border-border/10 shadow-soft-md hover:shadow-soft-lg transition-all space-y-4"
                >
                  {/* ... image and text ... */}
                  
                  {/* ... price ... */}
                  
                    {isOwner && (
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
                    )}
