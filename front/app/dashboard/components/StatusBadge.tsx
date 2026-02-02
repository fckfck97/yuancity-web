import React from "react";

export default function StatusBadge({ status }: { status: string }) {
  const configs: Record<string, { label: string; classes: string }> = {
    not_processed: {
      label: "Pendiente",
      classes: "bg-yellow-50 text-yellow-600 border-yellow-200",
    },
    processed: {
      label: "Procesado",
      classes: "bg-blue-50 text-blue-600 border-blue-200",
    },
    shipping: {
      label: "En camino",
      classes: "bg-indigo-50 text-indigo-600 border-indigo-200",
    },
    delivered: {
      label: "Entregado",
      classes: "bg-green-50 text-green-600 border-green-200",
    },
    cancelled: {
      label: "Cancelado",
      classes: "bg-red-50 text-red-600 border-red-200",
    },
  };

  const config = configs[status] || {
    label: status,
    classes: "bg-gray-50 text-gray-600 border-gray-200",
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border ${config.classes}`}
    >
      {config.label}
    </span>
  );
}
