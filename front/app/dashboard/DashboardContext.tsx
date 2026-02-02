"use client";

import React, { createContext, useContext, useMemo, useState } from "react";

type DashboardContextValue = {
  activeView: string;
  setActiveView: (view: string) => void;
  createProductRequest: number;
  requestCreateProduct: () => void;
};

const DashboardContext = createContext<DashboardContextValue | null>(null);

export function DashboardProvider({ children }: { children: React.ReactNode }) {
  const [activeView, setActiveView] = useState("summary");
  const [createProductRequest, setCreateProductRequest] = useState(0);

  const requestCreateProduct = () => {
    setActiveView("products");
    setCreateProductRequest((prev) => prev + 1);
  };

  const value = useMemo(
    () => ({
      activeView,
      setActiveView,
      createProductRequest,
      requestCreateProduct,
    }),
    [activeView, createProductRequest],
  );

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard() {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error("useDashboard must be used within DashboardProvider");
  }
  return context;
}
