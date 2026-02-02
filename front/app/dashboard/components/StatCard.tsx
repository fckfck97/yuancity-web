import React from "react";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";

export default function StatCard({
  title,
  value,
  icon,
  trend,
  trendUp,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  trend: string;
  trendUp: boolean;
}) {
  return (
    <div className="bg-white p-6 rounded-[2rem] border border-border/10 shadow-soft-lg hover:shadow-soft-xl transition-all duration-300 group">
      <div className="flex justify-between items-center mb-6">
        <div className="w-12 h-12 rounded-2xl bg-secondary/30 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
          {React.cloneElement(icon as React.ReactElement, { size: 24 })}
        </div>
        <div
          className={`flex items-center gap-1 text-[10px] font-black px-3 py-1.5 rounded-full border shadow-soft-sm ${
            trendUp
              ? "bg-green-50 text-green-600 border-green-100"
              : "bg-red-50 text-red-600 border-red-100"
          }`}
        >
          {trendUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {trend}
        </div>
      </div>

      <div className="space-y-1">
        <h4 className="text-muted-foreground text-xs font-bold uppercase tracking-widest">
          {title}
        </h4>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-black text-foreground tracking-tight">
            {value}
          </span>
        </div>
      </div>
    </div>
  );
}
