import React from "react";
import { Star } from "lucide-react";

interface ReviewsViewProps {
  reviews: any[];
}

export default function ReviewsView({ reviews }: ReviewsViewProps) {
  const average =
    reviews.length > 0
      ? reviews.reduce((acc: number, r: any) => acc + (r.rating || 0), 0) /
        reviews.length
      : 0;

  return (
    <div className="space-y-8">
      <div className="bg-white p-6 sm:p-8 rounded-[2.5rem] border border-border/10 shadow-soft-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <h2 className="text-2xl font-bold text-foreground uppercase tracking-tight">
            Opiniones de Clientes
          </h2>
          <div className="flex items-center gap-2 text-primary font-black bg-primary/5 px-4 py-2 rounded-xl border border-primary/10 shadow-soft-sm">
            <Star size={20} fill="currentColor" />
            <span className="text-lg">{average.toFixed(1)}</span>
          </div>
        </div>

        {reviews.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
            <div className="w-20 h-20 bg-secondary/30 rounded-full flex items-center justify-center text-muted-foreground">
              <Star size={40} />
            </div>
            <div className="space-y-1">
              <h3 className="text-xl font-bold">Sin valoraciones aún</h3>
              <p className="text-muted-foreground">
                Las opiniones de tus compradores aparecerán aquí.
              </p>
            </div>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {reviews.map((review: any) => (
              <div
                key={review.id}
                className="p-6 rounded-[2rem] bg-secondary/10 border border-border/5 space-y-4 hover:shadow-soft-md transition-all"
              >
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                      {(review.user_name || review.customer_name || "U")[0]}
                    </div>
                    <div>
                      <p className="font-bold text-sm text-foreground">
                        {review.user_name || review.customer_name || "Comprador"}
                      </p>
                      <p className="text-[10px] text-muted-foreground font-medium uppercase">
                        {new Date(review.date_created).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-0.5 text-yellow-500">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        size={14}
                        fill={i < (review.rating || 0) ? "currentColor" : "none"}
                        stroke="currentColor"
                      />
                    ))}
                  </div>
                </div>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  "{review.comment || "Sin comentarios."}"
                </p>
                <div className="pt-4 border-t border-border/5 flex items-center justify-between">
                  <span className="text-[10px] font-bold text-primary bg-primary/10 px-3 py-1 rounded-full uppercase">
                    {review.product_name || "Producto"}
                  </span>
                  <button className="text-xs font-bold text-muted-foreground hover:text-primary transition-colors">
                    Responder
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
