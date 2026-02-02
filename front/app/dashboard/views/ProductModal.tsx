import React from "react";
import { ChevronDown, Plus, Upload, X } from "lucide-react";

interface ProductModalProps {
  isOpen: boolean;
  isEditMode: boolean;
  isSubmitting: boolean;
  newProduct: {
    id: string;
    name: string;
    category: string;
    price: string;
    stock: string;
    description: string;
    images: any[];
  };
  dbCategories: any[];
  imagePreviews: string[];
  onClose: () => void;
  onFieldChange: (field: string, value: string) => void;
  onImageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onRemovePreview: (index: number) => void;
  onSave: () => void;
}

export default function ProductModal({
  isOpen,
  isEditMode,
  isSubmitting,
  newProduct,
  dbCategories,
  imagePreviews,
  onClose,
  onFieldChange,
  onImageChange,
  onRemovePreview,
  onSave,
}: ProductModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative w-full max-w-2xl bg-white rounded-[3rem] shadow-soft-2xl border border-border/10 overflow-hidden animate-in zoom-in duration-300">
        <div className="p-8 md:p-12 space-y-8 max-h-[90vh] overflow-y-auto scrollbar-none">
          <div className="flex justify-between items-start">
            <div className="space-y-1">
              <h3 className="text-3xl font-black text-foreground uppercase tracking-tighter">
                {isEditMode ? "Editar Mueble" : "Cargar Mueble"}
              </h3>
              <p className="text-muted-foreground font-medium">
                {isEditMode
                  ? "Actualiza los detalles del producto."
                  : "Completa los detalles para añadirlo al catálogo."}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 bg-secondary/30 rounded-xl hover:bg-secondary/50 transition-colors"
            >
              <X size={24} />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
                Nombre del Mueble
              </label>
              <input
                type="text"
                placeholder="Ej. Sofá Modular Nórdico"
                className="w-full h-14 px-6 bg-secondary/20 rounded-2xl border-none outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
                value={newProduct.name}
                onChange={(e) => onFieldChange("name", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
                Categoría
              </label>
              <div className="relative">
                <select
                  className="w-full h-14 px-6 bg-secondary/20 rounded-2xl border-none outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium appearance-none"
                  value={newProduct.category}
                  onChange={(e) => onFieldChange("category", e.target.value)}
                >
                  <option value="">Seleccionar...</option>
                  {dbCategories.map((cat: any) => (
                    <React.Fragment key={cat.id}>
                      <option value={cat.id}>{cat.name}</option>
                      {cat.sub_categories?.map((sub: any) => (
                        <option key={sub.id} value={sub.id}>
                          &nbsp;&nbsp;— {sub.name}
                        </option>
                      ))}
                    </React.Fragment>
                  ))}
                </select>
                <ChevronDown
                  className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground"
                  size={18}
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
                Precio Total
              </label>
              <input
                type="number"
                placeholder="0.00"
                className="w-full h-14 px-6 bg-secondary/20 rounded-2xl border-none outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
                value={newProduct.price}
                onChange={(e) => onFieldChange("price", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
                Stock Inicial
              </label>
              <input
                type="number"
                placeholder="1"
                className="w-full h-14 px-6 bg-secondary/20 rounded-2xl border-none outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
                value={newProduct.stock}
                onChange={(e) => onFieldChange("stock", e.target.value)}
              />
            </div>
            <div className="md:col-span-2 space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
                Descripción
              </label>
              <textarea
                placeholder="Detalles sobre materiales, dimensiones y cuidado..."
                className="w-full h-32 p-6 bg-secondary/20 rounded-[1.5rem] border-none outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium resize-none"
                value={newProduct.description}
                onChange={(e) => onFieldChange("description", e.target.value)}
              />
            </div>

            <div className="md:col-span-2 space-y-4">
              <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
                Imágenes del Producto
              </label>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {isEditMode &&
                  newProduct.images?.map((img: any, idx: number) => (
                    <div
                      key={img.id || idx}
                      className="relative aspect-square rounded-2xl overflow-hidden group border border-border/10"
                    >
                      <img
                        src={img.image}
                        alt="Producto"
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <span className="text-[10px] text-white font-bold uppercase">
                          Existente
                        </span>
                      </div>
                    </div>
                  ))}

                {imagePreviews.map((preview, idx) => (
                  <div
                    key={idx}
                    className="relative aspect-square rounded-2xl overflow-hidden border-2 border-primary/20"
                  >
                    <img
                      src={preview}
                      alt="Vista previa"
                      className="w-full h-full object-cover"
                    />
                    <button
                      onClick={() => onRemovePreview(idx)}
                      className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 transition-colors"
                    >
                      <X size={12} />
                    </button>
                  </div>
                ))}

                <label className="aspect-square rounded-2xl border-2 border-dashed border-border/20 flex flex-col items-center justify-center cursor-pointer hover:bg-secondary/10 transition-all group">
                  <Upload
                    className="text-muted-foreground group-hover:text-primary transition-colors"
                    size={24}
                  />
                  <span className="text-[10px] font-bold text-muted-foreground mt-2 uppercase">
                    Añadir
                  </span>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    className="hidden"
                    onChange={onImageChange}
                  />
                </label>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <button
              disabled={isSubmitting}
              className="flex-1 h-16 bg-primary text-white rounded-[1.5rem] shadow-soft-lg hover:shadow-soft-xl hover:scale-[1.02] disabled:opacity-50 disabled:scale-100 transition-all font-black uppercase tracking-widest flex items-center justify-center gap-2"
              onClick={onSave}
            >
              {isSubmitting ? (
                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              ) : (
                <Plus size={20} />
              )}
              {isEditMode ? "ACTUALIZAR" : "GUARDAR PRODUCTO"}
            </button>
            <button
              className="px-8 h-16 bg-white text-muted-foreground rounded-[1.5rem] border border-border/20 hover:bg-secondary/10 transition-all font-bold uppercase tracking-widest"
              onClick={onClose}
            >
              CANCELAR
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
