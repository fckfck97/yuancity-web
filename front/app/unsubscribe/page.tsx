"use client"

import { Suspense, useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import Navbar from "@/components/navigation/navbar"
import {
  ArrowLeft,
  Mail,
  CheckCircle,
  XCircle,
  Loader2,
  MailX,
  Clock,
  AlertCircle,
} from "lucide-react"
import Link from "next/link"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface UserData {
  id?: string
  email?: string
  full_name?: string
  unsubscribed?: boolean
}

function DesuscribirContent() {
  const searchParams = useSearchParams()

  const normalizeParam = (value: string | null) => (value || "").trim() || null

  const emailParam =
    normalizeParam(searchParams.get("email")) ??
    normalizeParam(searchParams.get("user_email"))

  const idParam =
    normalizeParam(searchParams.get("id")) ??
    normalizeParam(searchParams.get("user_id")) ??
    normalizeParam(searchParams.get("uid"))

  const [loading, setLoading] = useState(true)
  const [unsubscribing, setUnsubscribing] = useState(false)
  const [userData, setUserData] = useState<UserData | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [email, setEmail] = useState("")
  const [showForm, setShowForm] = useState(false)

  const [resolvedEmail, setResolvedEmail] = useState<string | null>(emailParam)
  const [resolvedId, setResolvedId] = useState<string | null>(idParam)

  useEffect(() => {
    setResolvedEmail(emailParam)
    setResolvedId(idParam)

    if (emailParam || idParam) {
      checkUnsubscribeStatus(emailParam, idParam)
    } else {
      setShowForm(true)
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [emailParam, idParam])

  const checkUnsubscribeStatus = async (
    emailValue?: string | null,
    idValue?: string | null
  ) => {
    const emailToCheck = (emailValue || email || "").trim() || null
    const idToCheck = (idValue || "").trim() || null

    if (!emailToCheck && !idToCheck) {
      setError("Por favor ingresa tu email")
      setLoading(false)
      return
    }

    setError(null)

    try {
      const query = new URLSearchParams()
      if (idToCheck) query.append("id", idToCheck)
      if (emailToCheck) query.append("email", emailToCheck)

      const res = await fetch(
        `${API_URL}/api/user/unsubscribe/?${query.toString()}`,
        { cache: "no-store" }
      )

      if (!res.ok) {
        if (res.status === 404) throw new Error("404")
        throw new Error("network")
      }

      const data: UserData = await res.json()
      setUserData(data)
      setResolvedEmail(data?.email || emailToCheck)
      setResolvedId(data?.id || idToCheck)
      setShowForm(false)
    } catch (err: any) {
      console.error("Error checking unsubscribe status:", err)
      if (err?.message === "404") {
        setError("Usuario no encontrado con ese email")
      } else {
        setError("Error al verificar estado")
      }
      setShowForm(true)
      setUserData(null)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitEmail = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) {
      setError("Por favor ingresa tu email")
      return
    }
    setLoading(true)
    setError(null)
    checkUnsubscribeStatus(email, null)
  }

  const handleUnsubscribe = async () => {
    const emailToUse = (resolvedEmail || userData?.email || email || "").trim() || null
    const idToUse = (resolvedId || userData?.id || "").trim() || null

    if (!emailToUse && !idToUse) return

    setUnsubscribing(true)
    setError(null)

    try {
      const body: Record<string, string> = {}
      if (idToUse) body.id = idToUse
      if (emailToUse) body.email = emailToUse

      const res = await fetch(`${API_URL}/api/user/unsubscribe/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })

      if (!res.ok) {
        if (res.status === 404) throw new Error("404")
        throw new Error("network")
      }

      const data: UserData = await res.json()
      setUserData(data)
      setResolvedEmail(data?.email || emailToUse)
      setResolvedId(data?.id || idToUse)
    } catch (err: any) {
      console.error("Error unsubscribing:", err)
      if (err?.message === "404") setError("Usuario no encontrado")
      else setError("Error al desuscribir. Intenta de nuevo.")
    } finally {
      setUnsubscribing(false)
    }
  }

  const PageShell = ({ children }: { children: React.ReactNode }) => (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: "var(--color-background)",
        color: "var(--color-foreground)",
      }}
    >
      <Navbar />
      <div className="container mx-auto px-4 py-24">{children}</div>
    </div>
  )

  const BackButton = () => (
    <Link
      href="/"
      className="inline-flex items-center mb-6 transition-colors hover:opacity-70"
      style={{ color: "var(--color-foreground)", opacity: 0.7 }}
    >
      <ArrowLeft className="mr-2 h-4 w-4" />
      Volver al Inicio
    </Link>
  )

  const Card = ({ children }: { children: React.ReactNode }) => (
    <div
      className="rounded-[2.5rem] shadow-2xl overflow-hidden"
      style={{
        backgroundColor: "var(--color-secondary-background)",
        border: "3px solid var(--color-border)",
      }}
    >
      {children}
    </div>
  )

  const ErrorBox = ({ message }: { message: string }) => (
    <div
      className="rounded-xl p-4"
      style={{
        border: "2px solid rgba(239,68,68,0.35)",
        backgroundColor: "rgba(239,68,68,0.10)",
      }}
    >
      <div className="flex items-center gap-2">
        <XCircle className="h-5 w-5" style={{ color: "rgb(248,113,113)" }} />
        <p className="text-sm" style={{ color: "var(--color-foreground)", opacity: 0.9 }}>
          {message}
        </p>
      </div>
    </div>
  )

  // Loading
  if (loading) {
    return (
      <PageShell>
        <div className="max-w-2xl mx-auto">
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="h-12 w-12 text-orange-500 animate-spin mb-4" />
            <p className="text-lg" style={{ opacity: 0.75 }}>
              Verificando...
            </p>
          </div>
        </div>
      </PageShell>
    )
  }

  // Show email input form (no params OR not found)
  if (showForm && !userData) {
    return (
      <PageShell>
        <div className="max-w-2xl mx-auto">
          <BackButton />

          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Desuscribirse</h1>
            <p className="mb-4" style={{ opacity: 0.75 }}>
              Ingresa tu email para gestionar tu suscripción
            </p>
          </div>

          <Card>
            <div className="p-8">
              <form onSubmit={handleSubmitEmail} className="space-y-6">
                <div>
                  <label htmlFor="email" className="block font-medium mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="tu@email.com"
                    className="w-full px-4 py-3 rounded-xl placeholder:text-gray-400 focus:outline-none focus:ring-2 transition-colors"
                    style={{
                      backgroundColor: "var(--color-background)",
                      color: "var(--color-foreground)",
                      border: "2px solid var(--color-border)",
                    }}
                    required
                  />
                </div>

                {error && <ErrorBox message={error} />}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 rounded-xl py-3 font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    backgroundColor: "var(--color-main)",
                    color: "var(--color-main-foreground)",
                  }}
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Verificando...
                    </>
                  ) : (
                    "Continuar"
                  )}
                </button>
              </form>
            </div>
          </Card>
        </div>
      </PageShell>
    )
  }

  // Global error (non-form flow)
  if (error && !showForm) {
    return (
      <PageShell>
        <div className="max-w-2xl mx-auto">
          <BackButton />

          <Card>
            <div className="p-8">
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 bg-red-500/15 rounded-full flex items-center justify-center mb-4 border border-red-500/25">
                  <XCircle className="h-8 w-8 text-red-400" />
                </div>
                <h1 className="text-2xl font-bold mb-2">Error</h1>
                <p className="mb-6" style={{ opacity: 0.75 }}>
                  {error}
                </p>
                <Link
                  href="/"
                  className="inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 font-semibold transition-colors"
                  style={{
                    backgroundColor: "var(--color-main)",
                    color: "var(--color-main-foreground)",
                  }}
                >
                  Volver al Inicio
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </PageShell>
    )
  }

  // Already unsubscribed
  if (userData?.unsubscribed) {
    return (
      <PageShell>
        <div className="max-w-2xl mx-auto">
          <BackButton />

          <Card>
            <div className="p-8">
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 bg-green-500/15 rounded-full flex items-center justify-center mb-4 border border-green-500/25">
                  <CheckCircle className="h-8 w-8 text-green-400" />
                </div>
                <h1 className="text-3xl font-bold mb-2">Ya estás desuscrito</h1>
                <p className="mb-2" style={{ opacity: 0.7 }}>
                  {userData.email}
                </p>

                <div
                  className="rounded-xl p-6 my-6 w-full"
                  style={{
                    backgroundColor: "var(--color-background)",
                    border: "2px solid var(--color-border)",
                  }}
                >
                  <p style={{ opacity: 0.8 }}>
                    Ya no recibirás correos de Mikiguiki. Si cambias de opinión,
                    puedes volver a suscribirte desde la configuración de tu cuenta.
                  </p>
                </div>

                <Link
                  href="/"
                  className="inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 font-semibold transition-colors"
                  style={{
                    backgroundColor: "var(--color-main)",
                    color: "var(--color-main-foreground)",
                  }}
                >
                  Volver al Inicio
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </PageShell>
    )
  }

  // Default: confirm unsubscribe
  return (
    <PageShell>
      <div className="max-w-2xl mx-auto">
        <BackButton />

        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Desuscribirse</h1>
          <p className="mb-4" style={{ opacity: 0.75 }}>
            Deja de recibir correos de Mikiguiki
          </p>

          <div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg"
            style={{
              backgroundColor: "var(--color-secondary-background)",
              border: "2px solid var(--color-border)",
            }}
          >
            <Clock className="h-4 w-4 text-orange-500" />
            <span className="text-sm" style={{ opacity: 0.7 }}>
              Última actualización: 20 de febrero de 2026
            </span>
          </div>
        </div>

        <div className="space-y-6">
          {/* Info del usuario */}
          <section
            className="rounded-2xl p-6"
            style={{
              backgroundColor: "var(--color-secondary-background)",
              border: "2px solid var(--color-border)",
            }}
          >
            <div className="flex items-center gap-3 mb-4">
              <Mail className="h-6 w-6 text-orange-500" />
              <h2 className="text-xl font-bold">Tu cuenta</h2>
            </div>
            {userData?.full_name && <p className="font-medium mb-1">{userData.full_name}</p>}
            {userData?.email && <p style={{ opacity: 0.7 }}>{userData.email}</p>}
          </section>

          {/* Qué dejarás de recibir */}
          <section
            className="rounded-2xl p-6"
            style={{
              backgroundColor: "var(--color-secondary-background)",
              border: "2px solid var(--color-border)",
            }}
          >
            <div className="flex items-center gap-3 mb-4">
              <MailX className="h-6 w-6 text-orange-500" />
              <h2 className="text-xl font-bold">
                Si te desuscribes, dejarás de recibir:
              </h2>
            </div>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <XCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
                <p style={{ opacity: 0.8 }}>Notificaciones de nuevos contenidos y estrenos</p>
              </div>
              <div className="flex items-start gap-3">
                <XCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
                <p style={{ opacity: 0.8 }}>Recomendaciones personalizadas</p>
              </div>
              <div className="flex items-start gap-3">
                <XCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
                <p style={{ opacity: 0.8 }}>Actualizaciones sobre nuevas funciones</p>
              </div>
            </div>
          </section>

          {/* Advertencia */}
          <section
            className="rounded-2xl p-6"
            style={{
              border: "2px solid rgba(249,115,22,0.45)",
              backgroundColor: "rgba(249,115,22,0.10)",
            }}
          >
            <div
              className="flex items-start gap-3 rounded-xl p-4"
              style={{ border: "1px solid rgba(249,115,22,0.45)" }}
            >
              <AlertCircle className="text-orange-400 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="font-semibold">Puedes volver cuando quieras</p>
                <p className="mt-1" style={{ opacity: 0.8 }}>
                  Esta acción se puede revertir en cualquier momento desde la configuración de tu cuenta.
                </p>
              </div>
            </div>
          </section>

          {/* Botones */}
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={handleUnsubscribe}
              disabled={unsubscribing}
              className="flex-1 flex items-center justify-center gap-2 rounded-xl px-6 py-3 font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ backgroundColor: "#dc2626", color: "#ffffff" }}
            >
              {unsubscribing ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Procesando...
                </>
              ) : (
                "Confirmar desuscripción"
              )}
            </button>

            <Link
              href="/"
              className="flex-1 flex items-center justify-center rounded-xl px-6 py-3 font-semibold transition-colors"
              style={{
                border: "2px solid var(--color-border)",
                color: "var(--color-foreground)",
              }}
            >
              Cancelar
            </Link>
          </div>

          <p className="text-sm text-center" style={{ opacity: 0.65 }}>
            Puedes volver a suscribirte en cualquier momento desde la configuración de tu cuenta.
          </p>
        </div>
      </div>
    </PageShell>
  )
}

function PageFallback() {
  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: "var(--color-background)",
        color: "var(--color-foreground)",
      }}
    >
      <Navbar />
      <div className="container mx-auto px-4 py-24">
        <div className="max-w-2xl mx-auto">
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="h-12 w-12 text-orange-500 animate-spin mb-4" />
            <p className="text-lg" style={{ opacity: 0.75 }}>
              Cargando...
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function DesuscribirPage() {
  return (
    <Suspense fallback={<PageFallback />}>
      <DesuscribirContent />
    </Suspense>
  )
}