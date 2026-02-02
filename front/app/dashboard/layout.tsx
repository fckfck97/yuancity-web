"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { loadAuth, loadUser, clearAuth } from "@/lib/auth";
import {
  LayoutGrid,
  Package,
  ShoppingCart,
  MessageCircle,
  Star,
  LogOut,
  Menu,
  X,
  Database,
  Plus,
  Users,
} from "lucide-react";
import { DashboardProvider, useDashboard } from "./DashboardContext";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <DashboardProvider>
      <DashboardShell>{children}</DashboardShell>
    </DashboardProvider>
  );
}

function DashboardShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { activeView, setActiveView, requestCreateProduct } = useDashboard();

  const [authorized, setAuthorized] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const auth = loadAuth();
    const currentUser = loadUser();

    if (!auth || !auth.access) {
      router.replace("/login");
      return;
    }

    if (currentUser) setUser(currentUser);
    setAuthorized(true);
  }, [router]);

  const handleLogout = () => {
    clearAuth();
    router.replace("/login");
  };

  const navItems = [
    { id: "summary", label: "Resumen", icon: LayoutGrid },
    { id: "products", label: "Productos", icon: Package },
    { id: "orders", label: "Compras", icon: ShoppingCart },
    { id: "vendors", label: "Vendedores", icon: Users },
    { id: "support", label: "Soporte", icon: MessageCircle },
    { id: "reviews", label: "Valoraciones", icon: Star },
  ];

  if (!authorized) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-secondary/5">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-sm font-bold text-muted-foreground uppercase tracking-widest">
          Verificando Acceso...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary/5 flex">
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-border/10">
        <div className="flex items-center justify-between px-6 py-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-xl bg-secondary/10 text-foreground"
          >
            <Menu size={20} />
          </button>

          <div className="flex items-center gap-2 font-black text-foreground text-sm tracking-tight">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white">
              <Database size={16} />
            </div>
            CREDIMUEBLE
          </div>

          <div className="w-9" />
        </div>
      </div>

      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/20 backdrop-blur-sm z-[60]"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={[
          "w-72 bg-white border-r border-border/10 flex flex-col h-screen z-[70]",
          "fixed md:sticky md:top-0",
          "transition-transform duration-500 ease-in-out",
          sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
        ].join(" ")}
      >
        <div className="p-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3 font-black text-foreground text-xl tracking-tight">
              <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white shadow-soft-lg">
                <Database size={20} />
              </div>
              PANEL
            </div>

            <button
              onClick={() => setSidebarOpen(false)}
              className="md:hidden p-2 rounded-xl bg-secondary/10 text-foreground"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        <nav className="flex-1 px-6 space-y-4 overflow-y-auto">
          <h3 className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] px-2">
            Secciones
          </h3>
          <div className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveView(item.id);
                    setSidebarOpen(false);
                  }}
                  className={`group flex items-center justify-between px-4 py-3.5 rounded-2xl text-sm font-bold transition-all w-full ${
                    isActive
                      ? "bg-primary text-white shadow-soft-lg"
                      : "text-muted-foreground hover:bg-white hover:text-foreground hover:shadow-soft-md border border-transparent hover:border-border/10"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={isActive ? "text-white" : "text-primary"}>
                      <Icon size={18} />
                    </span>
                    {item.label}
                  </div>
                </button>
              );
            })}
          </div>
        </nav>

        <div className="p-6">
          <div className="bg-secondary/10 p-4 rounded-[2rem] border border-border/5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-primary text-white flex items-center justify-center font-black shadow-soft-md">
                {user?.username?.[0]?.toUpperCase() || "U"}
              </div>
              <div className="flex-1 overflow-hidden">
                <p className="text-sm font-black text-foreground truncate">
                  {user?.username || "Usuario"}
                </p>
                <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest truncate">
                  {user?.role || "Admin"}
                </p>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-white rounded-xl text-xs font-black text-red-500 shadow-soft-sm hover:shadow-soft-md hover:bg-red-50 transition-all border border-red-100"
            >
              <LogOut size={14} />
              CERRAR SESIÓN
            </button>
          </div>
        </div>
      </aside>

      <main className="flex-1 min-w-0 p-6 md:p-12 mt-16 md:mt-0">
        <div className="max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
}
