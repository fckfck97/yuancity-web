"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { saveAuth, saveUser, loadAuth, buildApiUrl } from "@/lib/auth";
import { ENDPOINTS } from "@/lib/endpoints";
import Navbar from "@/components/navigation/navbar";
import Footer from "@/components/navigation/footer";
import { Mail, Lock, ArrowRight, ChevronLeft, Clock } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();

  // -------------------------
  // State
  // -------------------------
  const [step, setStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // OTP
  const OTP_LEN = 6;
  const [otp, setOtp] = useState<string[]>(
    Array.from({ length: OTP_LEN }, () => ""),
  );
  const otpInputs = useRef<Array<HTMLInputElement | null>>(
    Array(OTP_LEN).fill(null),
  );

  // Timer reenvío
  const [timer, setTimer] = useState(60);
  const [canResend, setCanResend] = useState(false);

  const otpValue = useMemo(() => otp.join(""), [otp]);

  // -------------------------
  // Helpers
  // -------------------------
  const resetMessages = () => {
    setError("");
    setSuccessMessage("");
  };

  const focusIndex = (i: number) => {
    otpInputs.current[i]?.focus();
  };

  const resetOtp = () => {
    setOtp(Array.from({ length: OTP_LEN }, () => ""));
    setTimeout(() => focusIndex(0), 0);
  };

  const setOtpAt = (i: number, val: string) => {
    setOtp((prev) => {
      const next = [...prev];
      next[i] = val;
      return next;
    });
  };

  // Rellena OTP desde un índice (soporta pegar 6 dígitos)
  const fillOtpFrom = (startIndex: number, raw: string) => {
    const chars = raw.replace(/\D/g, "").slice(0, OTP_LEN - startIndex).split("");
    if (chars.length === 0) return;

    setOtp((prev) => {
      const next = [...prev];
      chars.forEach((c, k) => {
        next[startIndex + k] = c;
      });
      return next;
    });

    const nextIndex = Math.min(startIndex + chars.length, OTP_LEN - 1);
    setTimeout(() => focusIndex(nextIndex), 0);
  };

  // -------------------------
  // Effects
  // -------------------------
  useEffect(() => {
    // Redireccionar si ya está logueado
    const auth = loadAuth();
    if (auth?.access) router.replace("/dashboard");
  }, [router]);

  useEffect(() => {
    // Al entrar al paso 2, reiniciar timer + otp y enfocar
    if (step === 2) {
      setTimer(60);
      setCanResend(false);
      resetOtp();
    } else {
      // Si vuelve al paso 1, limpia OTP/timer también
      setTimer(60);
      setCanResend(false);
      setOtp(Array.from({ length: OTP_LEN }, () => ""));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step]);

  useEffect(() => {
    // Cuenta regresiva del timer (solo en step 2)
    if (step !== 2) return;
    if (timer <= 0) return;

    const interval = setInterval(() => {
      setTimer((prev) => {
        if (prev <= 1) {
          setCanResend(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [step, timer]);

  // -------------------------
  // Handlers API
  // -------------------------
  const handleRequestOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();

    const normalizedEmail = email.trim();
    if (!normalizedEmail) {
      setError("Ingresa tu correo.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(buildApiUrl(ENDPOINTS.LOGIN_OTP_REQUEST), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: normalizedEmail }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data?.detail || "Error al solicitar código.");
      }

      setSuccessMessage("Hemos enviado un código a tu correo.");
      setStep(2);
    } catch (err: any) {
      setError(err?.message || "Error de conexión");
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    if (!canResend || loading) return;

    resetMessages();
    setLoading(true);

    try {
      const res = await fetch(buildApiUrl(ENDPOINTS.LOGIN_OTP_REQUEST), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data?.detail || "Error al reenviar código.");
      }

      setSuccessMessage("Código reenviado exitosamente.");
      setTimer(60);
      setCanResend(false);
      resetOtp();
    } catch (err: any) {
      setError(err?.message || "Error al reenviar código");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();

    if (otpValue.length !== OTP_LEN || otp.some((d) => !d)) {
      setError("Ingresa el código completo de 6 dígitos.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(buildApiUrl(ENDPOINTS.LOGIN_OTP_VERIFY), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier: email.trim(),
          otp: otpValue,
          source: "web",
        }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data?.detail || "Código incorrecto.");
      }

      saveAuth(data);
      saveUser({
        username: email.trim(),
        role: "Vendedor",
      });

      router.replace("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Error de verificación");
    } finally {
      setLoading(false);
    }
  };

  // -------------------------
  // Handlers OTP inputs
  // -------------------------
  const handleOtpChange = (index: number, raw: string) => {
    // Soporta pegar varios dígitos en un input
    const digits = raw.replace(/\D/g, "");
    if (!digits) {
      setOtpAt(index, "");
      return;
    }

    if (digits.length === 1) {
      setOtpAt(index, digits);
      if (index < OTP_LEN - 1) focusIndex(index + 1);
      return;
    }

    // Pegar múltiple
    fillOtpFrom(index, digits);
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace") {
      // Si hay algo en el campo, lo borra
      if (otp[index]) {
        setOtpAt(index, "");
        return;
      }
      // Si está vacío, retrocede y borra el anterior
      if (index > 0) {
        setOtpAt(index - 1, "");
        focusIndex(index - 1);
      }
      return;
    }

    if (e.key === "ArrowLeft" && index > 0) {
      e.preventDefault();
      focusIndex(index - 1);
    }

    if (e.key === "ArrowRight" && index < OTP_LEN - 1) {
      e.preventDefault();
      focusIndex(index + 1);
    }
  };

  const handleOtpPaste = (index: number, e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const text = e.clipboardData.getData("text");
    fillOtpFrom(index, text);
  };

  const handleChangeEmail = () => {
    resetMessages();
    setStep(1);
    setOtp(Array.from({ length: OTP_LEN }, () => ""));
    setTimer(60);
    setCanResend(false);
  };

  // -------------------------
  // UI
  // -------------------------
  return (
    <div className="flex min-h-screen flex-col" style={{ backgroundColor: "var(--color-background)" }}>
      <Navbar />

      <main className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-[440px] animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div
            className="rounded-[2.5rem] shadow-2xl overflow-hidden p-8 md:p-12 space-y-8"
            style={{
              backgroundColor: "var(--color-secondary-background)",
              border: "3px solid var(--color-border)",
            }}
          >
            {/* Header */}
            <div className="text-center space-y-2">
              <div
                className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg"
                style={{ backgroundColor: "var(--color-main)" }}
              >
                {step === 1 ? <Mail size={36} className="text-white" /> : <Lock size={36} className="text-white" />}
              </div>

              <h1 className="text-3xl font-black uppercase tracking-tight" style={{ color: "var(--color-foreground)" }}>
                {step === 1 ? "Bienvenido" : "Verificación"}
              </h1>

              <p className="font-medium" style={{ color: "var(--color-foreground)", opacity: 0.7 }}>
                {step === 1
                  ? "Ingresa tu correo para continuar"
                  : `Ingresa el código enviado a ${email.trim() || "tu correo"}`}
              </p>
            </div>

            {/* Mensajes */}
            {error && (
              <div
                className="p-4 rounded-2xl text-sm font-bold text-center animate-shake"
                style={{
                  backgroundColor: "#fee",
                  color: "#c00",
                  border: "2px solid #fcc",
                }}
              >
                {error}
              </div>
            )}

            {successMessage && step === 2 && (
              <div
                className="p-4 rounded-2xl text-sm font-bold text-center"
                style={{
                  backgroundColor: "#ecfdf5",
                  color: "#047857",
                  border: "2px solid #a7f3d0",
                }}
              >
                {successMessage}
              </div>
            )}

            {/* Step 1 */}
            {step === 1 ? (
              <form onSubmit={handleRequestOTP} className="space-y-6">
                <div className="space-y-2">
                  <label
                    className="text-xs font-black uppercase tracking-widest ml-1"
                    style={{ color: "var(--color-foreground)", opacity: 0.6 }}
                  >
                    Correo Electrónico
                  </label>

                  <div className="relative">
                    <Mail
                      className="absolute left-4 top-1/2 -translate-y-1/2"
                      size={18}
                      style={{ color: "var(--color-main)" }}
                    />

                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full h-16 pl-12 pr-4 rounded-2xl outline-none transition-all font-bold"
                      style={{
                        backgroundColor: "var(--color-background)",
                        color: "var(--color-foreground)",
                        border: "2px solid var(--color-border)",
                      }}
                      placeholder="tu@correo.com"
                      required
                      onFocus={(e) => (e.currentTarget.style.borderColor = "var(--color-main)")}
                      onBlur={(e) => (e.currentTarget.style.borderColor = "var(--color-border)")}
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full h-16 rounded-2xl font-black uppercase tracking-widest shadow-lg hover:shadow-2xl hover:scale-[1.02] transition-all flex items-center justify-center gap-3 disabled:opacity-50"
                  style={{
                    backgroundColor: "var(--color-main)",
                    color: "var(--color-main-foreground)",
                  }}
                >
                  {loading ? (
                    "Enviando..."
                  ) : (
                    <>
                      Solicitar Código
                      <ArrowRight size={20} />
                    </>
                  )}
                </button>
              </form>
            ) : (
              // Step 2
              <form onSubmit={handleVerifyOTP} className="space-y-8">
                {/* OTP inputs */}
                <div className="space-y-4">
                  <div className="flex justify-between gap-2 md:gap-3">
                    {otp.map((digit, index) => (
                      <input
                        key={index}
                        ref={(el) => {
                          otpInputs.current[index] = el;
                        }}
                        value={digit}
                        onChange={(e) => handleOtpChange(index, e.target.value)}
                        onKeyDown={(e) => handleOtpKeyDown(index, e)}
                        onPaste={(e) => handleOtpPaste(index, e)}
                        className="w-full h-16 md:h-20 rounded-2xl text-center text-3xl font-black outline-none transition-all"
                        style={{
                          backgroundColor: "var(--color-background)",
                          color: "var(--color-main)",
                          border: "3px solid var(--color-border)",
                        }}
                        maxLength={1}
                        inputMode="numeric"
                        autoComplete="one-time-code"
                        onFocus={(e) => {
                          e.currentTarget.style.borderColor = "var(--color-main)";
                          e.currentTarget.select?.();
                        }}
                        onBlur={(e) => (e.currentTarget.style.borderColor = "var(--color-border)")}
                      />
                    ))}
                  </div>

                  {/* Timer / Resend */}
                  <div className="text-center">
                    {!canResend ? (
                      <div
                        className="flex items-center justify-center gap-2 font-bold text-sm"
                        style={{ color: "var(--color-foreground)", opacity: 0.7 }}
                      >
                        <Clock size={16} style={{ color: "var(--color-main)" }} />
                        Reenviar código en {timer}s
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={handleResendOTP}
                        disabled={loading}
                        className="font-bold text-sm hover:underline transition-all disabled:opacity-50"
                        style={{ color: "var(--color-main)" }}
                      >
                        Reenviar código
                      </button>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full h-16 rounded-2xl font-black uppercase tracking-widest shadow-lg hover:shadow-2xl hover:scale-[1.02] transition-all disabled:opacity-50"
                    style={{
                      backgroundColor: "var(--color-main)",
                      color: "var(--color-main-foreground)",
                    }}
                  >
                    {loading ? "Verificando..." : "Ingresar Ahora"}
                  </button>

                  <button
                    type="button"
                    onClick={handleChangeEmail}
                    className="w-full h-14 bg-transparent font-bold flex items-center justify-center gap-2 transition-all hover:opacity-70"
                    style={{ color: "var(--color-foreground)", opacity: 0.6 }}
                  >
                    <ChevronLeft size={18} />
                    Cambiar Correo
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Footer mini */}
          <div className="mt-8 text-center space-y-4">
            <div
              className="flex items-center justify-center gap-4 opacity-50"
              style={{ color: "var(--color-foreground)" }}
            >
              <div className="h-px w-8 bg-current" />
              <span className="text-[10px] font-black uppercase tracking-[0.2em]">
                YuanCity 2026
              </span>
              <div className="h-px w-8 bg-current" />
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
