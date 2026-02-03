import React, { useState } from "react";
import {
  MessageCircle,
  Mail,
  Calendar,
  Package,
  Image as ImageIcon,
} from "lucide-react";
import { buildApiUrl } from "@/lib/auth";

interface SupportTicket {
  id: number;
  subject: string;
  message: string;
  status: string;
  created_at: string;
  updated_at: string;
  user_email: string;
  user_name: string;
  order_id: string | null;
  images: Array<{ id: number; image: string }>;
}

interface SupportViewProps {
  tickets: SupportTicket[];
}

export default function SupportView({ tickets }: SupportViewProps) {
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(
    null,
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "in_progress":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "resolved":
        return "bg-green-100 text-green-800 border-green-200";
      case "closed":
        return "bg-gray-100 text-gray-800 border-gray-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="bg-white rounded-[2.5rem] border border-border/10 shadow-soft-xl overflow-hidden min-h-[600px] flex flex-col lg:flex-row">
      {/* Tickets List */}
      <div className="w-full lg:w-96 border-b lg:border-b-0 lg:border-r border-border/10 flex flex-col">
        <div className="p-6 border-b border-border/10 bg-secondary/5">
          <h3 className="text-lg font-bold text-foreground">
            Tickets de Soporte
          </h3>
          <p className="text-xs text-muted-foreground">
            {tickets.length} ticket{tickets.length !== 1 ? "s" : ""} en total
          </p>
        </div>
        <div className="flex-1 overflow-y-auto">
          {tickets.length === 0 ? (
            <div className="p-10 text-center text-muted-foreground text-sm">
              No hay tickets de soporte
            </div>
          ) : (
            tickets.map((ticket) => (
              <button
                key={ticket.id}
                onClick={() => setSelectedTicket(ticket)}
                className={`w-full p-4 flex flex-col gap-2 border-b border-border/5 hover:bg-secondary/10 transition-colors text-left ${
                  selectedTicket?.id === ticket.id
                    ? "bg-primary/5 border-l-4 border-l-primary"
                    : ""
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <div className="w-10 h-10 rounded-xl bg-secondary/30 flex items-center justify-center text-primary flex-shrink-0">
                      <MessageCircle size={20} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold text-foreground truncate">
                        {ticket.user_name || ticket.user_email}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">
                        {ticket.subject}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`text-[9px] px-2 py-1 rounded-full border font-semibold uppercase ${getStatusColor(
                      ticket.status,
                    )}`}
                  >
                    {ticket.status}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-muted-foreground ml-12">
                  <span className="flex items-center gap-1">
                    <Calendar size={10} />
                    {formatDate(ticket.created_at)}
                  </span>
                  {ticket.images.length > 0 && (
                    <span className="flex items-center gap-1">
                      <ImageIcon size={10} />
                      {ticket.images.length}
                    </span>
                  )}
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Ticket Details */}
      <div className="flex-1 flex flex-col bg-secondary/5">
        {selectedTicket ? (
          <>
            <div className="p-6 border-b border-border/10 bg-white">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <h4 className="font-bold text-xl text-foreground mb-1">
                    {selectedTicket.subject}
                  </h4>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Mail size={14} />
                      {selectedTicket.user_email}
                    </span>
                    {selectedTicket.order_id && (
                      <span className="flex items-center gap-1">
                        <Package size={14} />
                        Pedido #{selectedTicket.order_id.slice(0, 8)}
                      </span>
                    )}
                  </div>
                </div>
                <span
                  className={`px-3 py-1.5 rounded-full border font-semibold text-xs uppercase ${getStatusColor(
                    selectedTicket.status,
                  )}`}
                >
                  {selectedTicket.status}
                </span>
              </div>
              <div className="text-xs text-muted-foreground flex gap-4">
                <span>Creado: {formatDate(selectedTicket.created_at)}</span>
                <span>
                  Actualizado: {formatDate(selectedTicket.updated_at)}
                </span>
              </div>
            </div>

            <div className="flex-1 p-6 overflow-y-auto space-y-6">
              {/* Message */}
              <div className="bg-white rounded-2xl p-6 shadow-soft-sm border border-border/10">
                <h5 className="font-semibold text-sm text-muted-foreground mb-3">
                  Mensaje del Usuario
                </h5>
                <p className="text-foreground whitespace-pre-wrap">
                  {selectedTicket.message}
                </p>
              </div>

              {/* Images */}
              {selectedTicket.images.length > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-soft-sm border border-border/10">
                  <h5 className="font-semibold text-sm text-muted-foreground mb-3">
                    Imágenes Adjuntas ({selectedTicket.images.length})
                  </h5>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {selectedTicket.images.map((img) => (
                      <a
                        key={img.id}
                        href={buildApiUrl(img.image)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group relative aspect-square rounded-xl overflow-hidden border border-border/10 hover:shadow-soft-md transition-all"
                      >
                        <img
                          src={buildApiUrl(img.image)}
                          alt="Ticket attachment"
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                          <ImageIcon
                            className="text-white opacity-0 group-hover:opacity-100 transition-opacity"
                            size={24}
                          />
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4 opacity-50">
            <div className="w-20 h-20 rounded-full bg-secondary/30 flex items-center justify-center text-muted-foreground">
              <MessageCircle size={40} />
            </div>
            <p className="text-sm font-medium">
              Selecciona un ticket para ver los detalles
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
