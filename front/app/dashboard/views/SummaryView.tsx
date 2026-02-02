import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { DollarSign, Users, Package, TrendingUp } from "lucide-react";
import StatCard from "../components/StatCard";

interface SummaryViewProps {
  summaryData: {
    totalSales: number;
    totalClients: number;
    totalStock: number;
    avgPrice: number;
  };
  salesData: Array<{ month: string; sales: number; clients: number }>;
  categoryData: Array<{ name: string; value: number; color: string }>;
}

export default function SummaryView({
  summaryData,
  salesData,
  categoryData,
}: SummaryViewProps) {
  return (
    <div className="space-y-10">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Ventas Totales"
          value={`$${summaryData.totalSales.toLocaleString()}`}
          icon={<DollarSign />}
          trend="+12.5%"
          trendUp
        />
        <StatCard
          title="Clientes"
          value={summaryData.totalClients.toString()}
          icon={<Users />}
          trend="+8.2%"
          trendUp
        />
        <StatCard
          title="Stock Total"
          value={summaryData.totalStock.toString()}
          icon={<Package />}
          trend="-2.1%"
          trendUp={false}
        />
        <StatCard
          title="Ticket Promedio"
          value={`$${Math.round(summaryData.avgPrice)}`}
          icon={<TrendingUp />}
          trend="+5.7%"
          trendUp
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white p-6 sm:p-8 rounded-[2.5rem] border border-border/10 shadow-soft-lg">
          <div className="flex justify-between items-center mb-8">
            <h3 className="text-xl font-bold text-foreground uppercase tracking-tight">
              Rendimiento Mensual
            </h3>
          </div>
          <div className="h-[280px] sm:h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={salesData}>
                <defs>
                  <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                    <stop
                      offset="5%"
                      stopColor="hsl(var(--primary))"
                      stopOpacity={0.1}
                    />
                    <stop
                      offset="95%"
                      stopColor="hsl(var(--primary))"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#e2e8f0"
                />
                <XAxis
                  dataKey="month"
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fontSize: 12,
                    fill: "#94a3b8",
                    fontWeight: 600,
                  }}
                  dy={10}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fontSize: 12,
                    fill: "#94a3b8",
                    fontWeight: 600,
                  }}
                />
                <RechartsTooltip
                  contentStyle={{
                    borderRadius: "1rem",
                    border: "none",
                    boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.1)",
                    padding: "1rem",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="sales"
                  stroke="hsl(var(--primary))"
                  strokeWidth={4}
                  fillOpacity={1}
                  fill="url(#colorSales)"
                  activeDot={{
                    r: 6,
                    strokeWidth: 0,
                    fill: "hsl(var(--primary))",
                  }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 sm:p-8 rounded-[2.5rem] border border-border/10 shadow-soft-lg flex flex-col items-center">
          <h3 className="text-xl font-bold text-foreground uppercase tracking-tight mb-8 self-start">
            Categorías
          </h3>
          {categoryData.length === 0 ? (
            <div className="flex-1 w-full h-[260px] sm:h-[280px] flex items-center justify-center text-center text-muted-foreground text-sm">
              No hay categorías con productos asignados.
            </div>
          ) : (
            <div className="h-[260px] sm:h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={10}
                    dataKey="value"
                    stroke="none"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: "20px" }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
