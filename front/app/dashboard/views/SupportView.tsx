import React from "react";
import { Package, Users, MessageCircle, ArrowUpRight } from "lucide-react";
import StatusBadge from "../components/StatusBadge";

interface SupportViewProps {
  orders: any[];
  selectedOrderChat: any | null;
  chatMessages: any[];
  newMessage: string;
  onSelectChat: (order: any) => void;
  onMessageChange: (value: string) => void;
  onSendMessage: () => void;
}

export default function SupportView({
  orders,
  selectedOrderChat,
  chatMessages,
  newMessage,
  onSelectChat,
  onMessageChange,
  onSendMessage,
}: SupportViewProps) {
  return (
    <div className="bg-white rounded-[2.5rem] border border-border/10 shadow-soft-xl overflow-hidden min-h-[600px] flex flex-col lg:flex-row">
      <div className="w-full lg:w-80 border-b lg:border-b-0 lg:border-r border-border/10 flex flex-col">
        <div className="p-6 border-b border-border/10 bg-secondary/5">
          <h3 className="text-lg font-bold text-foreground">Conversaciones</h3>
          <p className="text-xs text-muted-foreground">
            Chats de pedidos activos
          </p>
        </div>
        <div className="flex-1 overflow-y-auto">
          {orders.length === 0 ? (
            <div className="p-10 text-center text-muted-foreground text-sm">
              No hay pedidos disponibles
            </div>
          ) : (
            orders.map((order: any) => (
              <button
                key={order.order_id}
                onClick={() => onSelectChat(order)}
                className={`w-full p-4 flex items-center gap-3 border-b border-border/5 hover:bg-secondary/10 transition-colors text-left ${
                  selectedOrderChat?.order_id === order.order_id
                    ? "bg-primary/5 border-l-4 border-l-primary"
                    : ""
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-secondary/30 flex items-center justify-center text-primary">
                  <Package size={20} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-baseline">
                    <p className="text-sm font-bold text-foreground truncate">
                      {order.customer_name}
                    </p>
                    <span className="text-[9px] text-muted-foreground">
                      {new Date(order.date_issued).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground truncate">
                    Ref: #{order.transaction_id.slice(0, 8)}
                  </p>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col bg-secondary/5">
        {selectedOrderChat ? (
          <>
            <div className="p-6 border-b border-border/10 bg-white flex justify-between items-center">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
                  <Users size={24} />
                </div>
                <div>
                  <h4 className="font-bold text-foreground">
                    {selectedOrderChat.customer_name}
                  </h4>
                  <p className="text-xs text-muted-foreground">
                    Pedido #{selectedOrderChat.transaction_id.slice(0, 8)}
                  </p>
                </div>
              </div>
              <StatusBadge status={selectedOrderChat.status} />
            </div>

            <div className="flex-1 p-6 overflow-y-auto space-y-4">
              {chatMessages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground space-y-2 opacity-60">
                  <MessageCircle size={40} className="mx-auto" />
                  <p className="text-sm">No hay mensajes aún en este chat.</p>
                </div>
              ) : (
                chatMessages.map((msg: any) => {
                  const isMe =
                    msg.sender_role === "vendor" ||
                    msg.sender_id === "vendor_id";
                  return (
                    <div
                      key={msg.id}
                      className={`flex ${isMe ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[80%] sm:max-w-[70%] p-4 rounded-3xl text-sm ${
                          isMe
                            ? "bg-primary text-primary-foreground rounded-br-none shadow-soft-sm"
                            : "bg-white text-foreground rounded-bl-none border border-border/10 shadow-soft-sm"
                        }`}
                      >
                        <p>{msg.message}</p>
                        <span
                          className={`text-[9px] mt-1 block ${
                            isMe
                              ? "text-primary-foreground/60"
                              : "text-muted-foreground"
                          }`}
                        >
                          {new Date(msg.created_at).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            <div className="p-6 bg-white border-t border-border/10 flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => onMessageChange(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && onSendMessage()}
                placeholder="Escribe un mensaje..."
                className="flex-1 h-12 px-6 bg-secondary/20 rounded-2xl outline-none focus:ring-2 focus:ring-primary/20 transition-all font-medium"
              />
              <button
                onClick={onSendMessage}
                className="w-full sm:w-12 h-12 bg-primary text-primary-foreground rounded-2xl flex items-center justify-center shadow-soft-md hover:shadow-soft-lg transition-all"
              >
                <ArrowUpRight size={20} />
              </button>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4 opacity-50">
            <div className="w-20 h-20 rounded-full bg-secondary/30 flex items-center justify-center text-muted-foreground">
              <MessageCircle size={40} />
            </div>
            <p className="text-sm font-medium">
              Selecciona una conversación para comenzar
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
