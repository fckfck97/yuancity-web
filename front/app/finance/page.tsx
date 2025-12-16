'use client'

import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Spinner } from '@/components/ui/spinner'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

type FinanceSession = {
  access: string
  refresh: string
  user: {
    id: string
    email: string
    full_name?: string
  }
}

type FinanceOrderItem = {
  id: string
  name: string
  price: string
  count: number
  vendor_name?: string | null
  vendor_email?: string | null
  vendor_earnings: string
}

type FinanceOrder = {
  id: string
  transaction_id: string
  status: string
  status_label: string
  amount: string
  buyer_email: string
  buyer_name: string
  date_issued: string
  city: string
  state_province_region: string
  country_region: string
  telephone_number: string
  items: FinanceOrderItem[]
  total_platform_fee: string
  vendor_total: string
}

type FinanceBankAccount = {
  bank_name: string
  account_type: string
  account_number: string
  account_holder_name: string
  document_type: string
  document_number: string
}

type FinancePayout = {
  id: string
  status: string
  status_label: string
  net_amount: string
  gross_amount: string
  platform_fee: string
  order_transaction_id: string
  vendor_email: string
  vendor_name: string
  vendor_phone: string
  bank_account?: FinanceBankAccount | null
  buyer_confirmed_at?: string | null
  available_on?: string | null
  released_at?: string | null
  notes?: string | null
}

type DashboardStats = {
  orders_total: number
  orders_pending: number
  payouts_waiting: number
  payouts_pending: number
  payouts_available: number
  payouts_released: number
  pending_amount: string
  available_amount: string
}

type DashboardPayload = {
  stats: DashboardStats
  recent_orders: FinanceOrder[]
  recent_payouts: FinancePayout[]
}

type Banner = {
  type: 'success' | 'error'
  message: string
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') ?? 'https://greencloset.shop'
const STORAGE_KEY = 'greencloset-finance-portal'

const payoutStatusOptions = [
  { value: 'waiting_confirmation', label: 'Esperando confirmación' },
  { value: 'pending_clearance', label: 'En verificación' },
  { value: 'available', label: 'Liberados' },
  { value: 'released', label: 'Pagados' },
  { value: 'all', label: 'Todos' },
]

const orderStatusOptions = [
  { value: 'not_processed', label: 'Recibidos' },
  { value: 'processed', label: 'Empacando' },
  { value: 'shipping', label: 'En camino' },
  { value: 'delivered', label: 'Entregados' },
  { value: 'cancelled', label: 'Cancelados' },
  { value: 'all', label: 'Todos' },
]

const payoutStatusVariants: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  waiting_confirmation: 'secondary',
  pending_clearance: 'outline',
  available: 'default',
  released: 'secondary',
  cancelled: 'destructive',
}

const orderStatusVariants: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  not_processed: 'secondary',
  processed: 'default',
  shipping: 'default',
  delivered: 'secondary',
  cancelled: 'destructive',
}

const nextPayoutAction: Record<
  string,
  { label: string; status: string } | undefined
> = {
  waiting_confirmation: {
    label: 'Marcar en verificación',
    status: 'pending_clearance',
  },
  pending_clearance: {
    label: 'Liberar fondos',
    status: 'available',
  },
  available: {
    label: 'Confirmar transferencia',
    status: 'released',
  },
}

const moneyFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})

const formatMoney = (value: string | number | null | undefined) => {
  if (value === null || value === undefined || value === '') {
    return '-'
  }
  const numeric = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(numeric)) {
    return value.toString()
  }
  return moneyFormatter.format(numeric)
}

export default function FinancePortalPage() {
  const [session, setSession] = useState<FinanceSession | null>(null)
  const [banner, setBanner] = useState<Banner | null>(null)
  const [loginEmail, setLoginEmail] = useState('')
  const [loginError, setLoginError] = useState<string | null>(null)
  const [isLoggingIn, setIsLoggingIn] = useState(false)
  const [summary, setSummary] = useState<DashboardPayload | null>(null)
  const [payouts, setPayouts] = useState<FinancePayout[]>([])
  const [orders, setOrders] = useState<FinanceOrder[]>([])
  const [payoutFilter, setPayoutFilter] = useState('waiting_confirmation')
  const [orderFilter, setOrderFilter] = useState('not_processed')
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [loadingPayouts, setLoadingPayouts] = useState(false)
  const [loadingOrders, setLoadingOrders] = useState(false)
  const [pendingPayoutId, setPendingPayoutId] = useState<string | null>(null)

  useEffect(() => {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    try {
      const parsed: FinanceSession = JSON.parse(raw)
      if (parsed?.access && parsed?.user?.email) {
        setSession(parsed)
      }
    } catch (error) {
      console.warn('No se pudo restaurar la sesión del portal financiero', error)
      window.localStorage.removeItem(STORAGE_KEY)
    }
  }, [])

  useEffect(() => {
    if (!banner) return
    const timeout = window.setTimeout(() => setBanner(null), 5000)
    return () => window.clearTimeout(timeout)
  }, [banner])

  const authorizedRequest = useCallback(
    async (path: string, init?: RequestInit) => {
      if (!session?.access) {
        throw new Error('Tu sesión expiró, inicia sesión nuevamente.')
      }
      const headers = new Headers(init?.headers)
      headers.set('Content-Type', 'application/json')
      headers.set('Authorization', `JWT ${session.access}`)
      const response = await fetch(`${API_URL}${path}`, {
        ...init,
        headers,
      })
      if (!response.ok) {
        let detail = 'No pudimos completar la solicitud.'
        try {
          const data = await response.json()
          detail = data?.detail ?? JSON.stringify(data)
        } catch {
          detail = response.statusText
        }
        throw new Error(detail)
      }
      if (response.status === 204) {
        return null
      }
      return response.json()
    },
    [session?.access],
  )

  const fetchSummary = useCallback(async () => {
    if (!session) return
    setLoadingSummary(true)
    try {
      const data = (await authorizedRequest(
        '/api/payment/finance/dashboard/',
      )) as DashboardPayload
      setSummary(data)
    } catch (error) {
      console.error(error)
      setBanner({
        type: 'error',
        message:
          error instanceof Error
            ? error.message
            : 'No pudimos cargar los indicadores.',
      })
    } finally {
      setLoadingSummary(false)
    }
  }, [authorizedRequest, session])

  const fetchPayouts = useCallback(async () => {
    if (!session) return
    setLoadingPayouts(true)
    const params = new URLSearchParams()
    if (payoutFilter !== 'all') {
      params.set('status', payoutFilter)
    }
    try {
      const data = (await authorizedRequest(
        `/api/payment/finance/payouts/${params.size ? `?${params}` : ''}`,
      )) as { payouts: FinancePayout[] }
      setPayouts(data?.payouts ?? [])
    } catch (error) {
      console.error(error)
      setBanner({
        type: 'error',
        message:
          error instanceof Error
            ? error.message
            : 'No pudimos cargar los pagos.',
      })
    } finally {
      setLoadingPayouts(false)
    }
  }, [authorizedRequest, payoutFilter, session])

  const fetchOrders = useCallback(async () => {
    if (!session) return
    setLoadingOrders(true)
    const params = new URLSearchParams()
    if (orderFilter !== 'all') {
      params.set('status', orderFilter)
    }
    try {
      const data = (await authorizedRequest(
        `/api/payment/finance/orders/${params.size ? `?${params}` : ''}`,
      )) as { orders: FinanceOrder[] }
      setOrders(data?.orders ?? [])
    } catch (error) {
      console.error(error)
      setBanner({
        type: 'error',
        message:
          error instanceof Error
            ? error.message
            : 'No pudimos cargar las órdenes.',
      })
    } finally {
      setLoadingOrders(false)
    }
  }, [authorizedRequest, orderFilter, session])

  useEffect(() => {
    if (!session) return
    fetchSummary()
  }, [session, fetchSummary])

  useEffect(() => {
    if (!session) return
    fetchPayouts()
  }, [session, payoutFilter, fetchPayouts])

  useEffect(() => {
    if (!session) return
    fetchOrders()
  }, [session, orderFilter, fetchOrders])

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault()
    setLoginError(null)
    setIsLoggingIn(true)
    try {
      const response = await fetch(`${API_URL}/api/payment/finance/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginEmail.trim() }),
      })
      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(data?.detail ?? 'Correo no autorizado.')
      }
      const data = (await response.json()) as FinanceSession
      const payload: FinanceSession = {
        access: data.access,
        refresh: data.refresh,
        user: data.user,
      }
      setSession(payload)
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
      setLoginEmail('')
      setBanner({ type: 'success', message: 'Sesión iniciada correctamente.' })
    } catch (error) {
      setLoginError(
        error instanceof Error ? error.message : 'No fue posible iniciar sesión.',
      )
    } finally {
      setIsLoggingIn(false)
    }
  }

  const handleLogout = () => {
    setSession(null)
    setSummary(null)
    setOrders([])
    setPayouts([])
    window.localStorage.removeItem(STORAGE_KEY)
  }

  const handlePayoutAction = async (payoutId: string, targetStatus: string) => {
    setPendingPayoutId(payoutId)
    try {
      await authorizedRequest(`/api/payment/finance/payouts/${payoutId}/status/`, {
        method: 'PATCH',
        body: JSON.stringify({ status: targetStatus }),
      })
      setBanner({
        type: 'success',
        message: 'El estado del pago se actualizó correctamente.',
      })
      fetchPayouts()
      fetchSummary()
    } catch (error) {
      setBanner({
        type: 'error',
        message:
          error instanceof Error
            ? error.message
            : 'No pudimos actualizar el pago.',
      })
    } finally {
      setPendingPayoutId(null)
    }
  }

  const payoutFilterOptions = useMemo(
    () => payoutStatusOptions.map((option) => option),
    [],
  )
  const orderFilterOptions = useMemo(
    () => orderStatusOptions.map((option) => option),
    [],
  )

  const renderBankAccount = (account?: FinanceBankAccount | null) => {
    if (!account) {
      return <span className="text-muted-foreground text-xs">Sin cuenta</span>
    }
    return (
      <div className="text-xs leading-tight">
        <p>{account.bank_name}</p>
        <p>{account.account_type === 'checking' ? 'Corriente' : 'Ahorros'}</p>
        <p className="font-medium">{account.account_number}</p>
        <p className="text-muted-foreground">
          {account.account_holder_name} · {account.document_number}
        </p>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-muted/20 px-4 py-16">
        <div className="mx-auto max-w-md">
          <Card>
            <CardHeader>
              <CardTitle>Portal financiero</CardTitle>
              <CardDescription>
                Ingresa con el correo autorizado para revisar órdenes y pagos.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="flex flex-col gap-4" onSubmit={handleLogin}>
                <label className="space-y-2 text-sm font-medium">
                  <span>Correo autorizado</span>
                  <Input
                    type="email"
                    placeholder="finanzas@greencloset.shop"
                    value={loginEmail}
                    onChange={(event) => setLoginEmail(event.target.value)}
                    required
                  />
                </label>
                {loginError && (
                  <p className="text-sm text-destructive">{loginError}</p>
                )}
                <Button type="submit" disabled={isLoggingIn}>
                  {isLoggingIn ? <Spinner className="text-white" /> : 'Entrar'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-muted/15 px-4 py-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <header className="flex flex-col gap-3 rounded-xl border bg-background/80 p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Usuario</p>
            <p className="text-lg font-semibold leading-tight">
              {session.user.full_name || session.user.email}
            </p>
            <p className="text-sm text-muted-foreground">{session.user.email}</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={fetchSummary}>
              Actualizar datos
            </Button>
            <Button variant="destructive" onClick={handleLogout}>
              Cerrar sesión
            </Button>
          </div>
        </header>

        {banner && (
          <div
            className={`rounded-lg border p-3 text-sm ${
              banner.type === 'error'
                ? 'border-destructive/40 bg-destructive/10 text-destructive'
                : 'border-emerald-500/40 bg-emerald-500/10 text-emerald-600'
            }`}
          >
            {banner.message}
          </div>
        )}

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {loadingSummary ? (
            <Card>
              <CardContent className="flex h-24 items-center justify-center">
                <Spinner className="size-6" />
              </CardContent>
            </Card>
          ) : (
            <>
              <Card>
                <CardHeader>
                  <CardDescription>Órdenes activas</CardDescription>
                  <CardTitle className="text-3xl">
                    {summary?.stats.orders_pending ?? 0}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardDescription>Pagos por revisar</CardDescription>
                  <CardTitle className="text-3xl">
                    {summary?.stats.payouts_waiting ?? 0}
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {formatMoney(summary?.stats.pending_amount ?? '0')}
                  </p>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardDescription>Pagos disponibles</CardDescription>
                  <CardTitle className="text-3xl">
                    {summary?.stats.payouts_available ?? 0}
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {formatMoney(summary?.stats.available_amount ?? '0')}
                  </p>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardDescription>Pagos completados</CardDescription>
                  <CardTitle className="text-3xl">
                    {summary?.stats.payouts_released ?? 0}
                  </CardTitle>
                </CardHeader>
              </Card>
            </>
          )}
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <Card className="h-full">
            <CardHeader className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <CardTitle>Pagos a vendedores</CardTitle>
                <CardDescription>
                  Revisa y libera los pagos cuando la cuenta esté verificada.
                </CardDescription>
              </div>
              <Select value={payoutFilter} onValueChange={setPayoutFilter}>
                <SelectTrigger className="min-w-[200px]">
                  <SelectValue placeholder="Filtrar por estado" />
                </SelectTrigger>
                <SelectContent>
                  {payoutFilterOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardHeader>
            <CardContent className="space-y-4">
              {loadingPayouts ? (
                <div className="flex h-32 items-center justify-center">
                  <Spinner className="size-6" />
                </div>
              ) : payouts.length === 0 ? (
                <p className="text-center text-sm text-muted-foreground">
                  No hay pagos en este estado.
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Vendedor</TableHead>
                      <TableHead>Orden</TableHead>
                      <TableHead>Neto</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead>Cuenta</TableHead>
                      <TableHead />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {payouts.map((payout) => {
                      const action = nextPayoutAction[payout.status]
                      return (
                        <TableRow key={payout.id}>
                          <TableCell className="min-w-[160px]">
                            <p className="font-medium">{payout.vendor_name}</p>
                            <p className="text-xs text-muted-foreground">
                              {payout.vendor_email}
                            </p>
                            {payout.vendor_phone && (
                              <p className="text-xs text-muted-foreground">
                                {payout.vendor_phone}
                              </p>
                            )}
                          </TableCell>
                          <TableCell>
                            <p className="font-mono text-xs">
                              #{payout.order_transaction_id}
                            </p>
                          </TableCell>
                          <TableCell className="font-semibold">
                            {formatMoney(payout.net_amount)}
                          </TableCell>
                          <TableCell>
                            <Badge variant={payoutStatusVariants[payout.status] ?? 'outline'}>
                              {payout.status_label}
                            </Badge>
                          </TableCell>
                          <TableCell>{renderBankAccount(payout.bank_account)}</TableCell>
                          <TableCell className="text-right">
                            {action ? (
                              <Button
                                size="sm"
                                onClick={() =>
                                  handlePayoutAction(payout.id, action.status)
                                }
                                disabled={pendingPayoutId === payout.id}
                              >
                                {pendingPayoutId === payout.id ? (
                                  <Spinner className="text-white" />
                                ) : (
                                  action.label
                                )}
                              </Button>
                            ) : (
                              <span className="text-xs text-muted-foreground">
                                Sin acciones
                              </span>
                            )}
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          <Card className="h-full">
            <CardHeader className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <CardTitle>Órdenes</CardTitle>
                <CardDescription>
                  Identifica entregas pendientes y confirma la información con los vendedores.
                </CardDescription>
              </div>
              <Select value={orderFilter} onValueChange={setOrderFilter}>
                <SelectTrigger className="min-w-[200px]">
                  <SelectValue placeholder="Filtrar por estado" />
                </SelectTrigger>
                <SelectContent>
                  {orderFilterOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardHeader>
            <CardContent className="space-y-4">
              {loadingOrders ? (
                <div className="flex h-32 items-center justify-center">
                  <Spinner className="size-6" />
                </div>
              ) : orders.length === 0 ? (
                <p className="text-center text-sm text-muted-foreground">
                  No hay órdenes con este filtro.
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Orden</TableHead>
                      <TableHead>Cliente</TableHead>
                      <TableHead>Total</TableHead>
                      <TableHead>Vendedores</TableHead>
                      <TableHead>Estado</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {orders.map((order) => (
                      <TableRow key={order.id}>
                        <TableCell className="font-mono text-xs">
                          #{order.transaction_id}
                        </TableCell>
                        <TableCell>
                          <p className="font-medium">{order.buyer_name}</p>
                          <p className="text-xs text-muted-foreground">
                            {order.buyer_email}
                          </p>
                        </TableCell>
                        <TableCell>
                          <p className="font-semibold">{formatMoney(order.amount)}</p>
                          <p className="text-xs text-muted-foreground">
                            Envío: {formatMoney(order.total_platform_fee)}
                          </p>
                        </TableCell>
                        <TableCell className="space-y-1">
                          {order.items.map((item) => (
                            <div key={item.id} className="text-xs">
                              <p className="font-medium">{item.vendor_name}</p>
                              <p className="text-muted-foreground">
                                {item.vendor_email} ·{' '}
                                {formatMoney(item.vendor_earnings)}
                              </p>
                            </div>
                          ))}
                        </TableCell>
                        <TableCell>
                          <Badge variant={orderStatusVariants[order.status] ?? 'outline'}>
                            {order.status_label}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </section>

        {summary && (
          <section className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Últimos pagos trabajados</CardTitle>
                <CardDescription>Los últimos 5 movimientos registrados.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {summary.recent_payouts.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    Aún no hay movimientos recientes.
                  </p>
                ) : (
                  summary.recent_payouts.map((payout) => (
                    <div
                      key={payout.id}
                      className="flex items-center justify-between rounded-lg border p-3"
                    >
                      <div>
                        <p className="font-medium">{payout.vendor_name}</p>
                        <p className="text-xs text-muted-foreground">
                          #{payout.order_transaction_id}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{formatMoney(payout.net_amount)}</p>
                        <Badge
                          variant={payoutStatusVariants[payout.status] ?? 'outline'}
                        >
                          {payout.status_label}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Órdenes recientes</CardTitle>
                <CardDescription>Solicitudes que llegaron en los últimos días.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {summary.recent_orders.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No hay órdenes recientes registradas.
                  </p>
                ) : (
                  summary.recent_orders.map((order) => (
                    <div
                      key={order.id}
                      className="flex items-center justify-between rounded-lg border p-3"
                    >
                      <div>
                        <p className="font-medium">{order.buyer_name}</p>
                        <p className="text-xs text-muted-foreground">
                          #{order.transaction_id}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{formatMoney(order.amount)}</p>
                        <Badge
                          variant={orderStatusVariants[order.status] ?? 'outline'}
                        >
                          {order.status_label}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </section>
        )}
      </div>
    </div>
  )
}
