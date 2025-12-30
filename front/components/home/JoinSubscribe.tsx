// components/JoinSubscribe.tsx
"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { useTranslation } from 'react-i18next';
export default function JoinSubscribe() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error" | "">("");
  const { t } = useTranslation();
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    setMessage("");
    setMessageType("");

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/blog/newsletter/subscribe`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        }
      );

      const data = await res.json();

      if (res.ok) {
        setMessage(t("home.JoinSubscribe.subscriptionSuccess"));
        setMessageType("success");
        setEmail("");
      } else {
        setMessage(data.error || t("home.JoinSubscribe.subscriptionError"));
        setMessageType("error");
      }
    } catch (err) {
      setMessage(t("home.JoinSubscribe.connectionError"));
      setMessageType("error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="join" className="py-20 bg-main">
      <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
        <div className="bg-black text-white border-4 border-border shadow-[28px_28px_0px_0px_var(--color-border)] p-8 mb-8 transform rotate-1">
          <h2 className="text-5xl md:text-7xl font-bold text-white mb-6">
            {t("home.JoinSubscribe.newEpisode")}
          </h2>
          <p className="text-xl text-white font-medium mb-8">
            {t("home.JoinSubscribe.recentlyAdded")}
          </p>

          {/* Formulario (mismos estilos/endpoint que el footer) */}
          <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-4">
            <div className="flex flex-col sm:flex-row gap-3 w-full">
              <input
                type="email"
                placeholder={t("home.JoinSubscribe.emailPlaceholder")}
                aria-label={t("home.JoinSubscribe.emailPlaceholder")}
                className="flex-1 px-4 py-3 border-2 border-border bg-background text-foreground font-medium"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading}
                className="bg-chart-2 text-main-foreground px-8 py-3 border-2 border-border shadow-brutal hover:shadow-brutal-lg transition-all font-bold flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {t("home.JoinSubscribe.sending")}
                  </>
                ) : (
                  t("home.JoinSubscribe.subscribe")
                )}
              </button>
            </div>

            {message && (
              <p
                className={`text-sm font-medium ${
                  messageType === "success"
                    ? "text-green-300"
                    : messageType === "error"
                    ? "text-red-300"
                    : ""
                }`}
              >
                {message}
              </p>
            )}
          </form>
        </div>
      </div>
    </section>
  );
}
