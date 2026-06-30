import { createContext, useContext, useEffect, useMemo, useState } from "react";
import {
  BrowserRouter,
  Link,
  Navigate,
  NavLink,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";
import {
  Activity,
  BarChart3,
  CalendarDays,
  LogOut,
  Plus,
  Search,
  Settings,
  ShieldCheck,
  Soup,
  Trash2,
  User,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api, setToken } from "./api";


const AuthContext = createContext(null);

const todayISO = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const navItems = [
  { to: "/", label: "Dashboard", icon: Activity },
  { to: "/meals", label: "Meal Log", icon: Soup },
  { to: "/search", label: "Food Search", icon: Search },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/profile", label: "Profile", icon: User },
];


function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<AuthPage mode="login" />} />
          <Route path="/signup" element={<AuthPage mode="signup" />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}


function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mealRefreshKey, setMealRefreshKey] = useState(0);

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await api.me();
        setUser(data.user);
      } catch {
        setToken(null);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      async signup(payload) {
        const data = await api.signup(payload);
        setToken(data.token);
        setUser(data.user);
      },
      async login(payload) {
        const data = await api.login(payload);
        setToken(data.token);
        setUser(data.user);
      },
      async logout() {
        try {
          await api.logout();
        } catch {
          // Logging out locally still matters if the server token has already expired.
        }
        setToken(null);
        setUser(null);
      },
      setUser,
      mealRefreshKey,
      notifyMealsChanged() {
        setMealRefreshKey((currentKey) => currentKey + 1);
      },
    }),
    [user, loading, mealRefreshKey],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}


function useAuth() {
  return useContext(AuthContext);
}


function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <FullPageLoader label="Checking your session..." />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}


function AuthPage({ mode }) {
  const isSignup = mode === "signup";
  const auth = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!auth.loading && auth.user) {
      navigate("/");
    }
  }, [auth.loading, auth.user, navigate]);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isSignup) {
        await auth.signup(form);
      } else {
        await auth.login({ email: form.email, password: form.password });
      }
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-page text-ink">
      <section className="mx-auto grid min-h-screen max-w-6xl items-center gap-8 px-5 py-10 lg:grid-cols-[1fr_440px]">
        <div className="max-w-2xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-semibold shadow-sm">
            <ShieldCheck size={18} className="text-mint" />
            Database-backed sessions
          </div>
          <h1 className="text-4xl font-bold leading-tight sm:text-6xl">NutriTrack AI</h1>
          <p className="mt-5 text-lg leading-8 text-slate-600">
            Track Indian meals, estimate nutrition, and follow weekly calorie and protein trends
            from one clean full-stack dashboard.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="text-2xl font-bold">{isSignup ? "Create account" : "Welcome back"}</h2>
          <p className="mt-2 text-sm text-slate-500">
            {isSignup ? "Start tracking in under a minute." : "Log in to continue tracking."}
          </p>

          {error && <Alert message={error} />}

          <div className="mt-6 grid gap-4">
            {isSignup && (
              <TextField label="Name" value={form.name} onChange={(value) => setForm({ ...form, name: value })} />
            )}
            <TextField label="Email" type="email" value={form.email} onChange={(value) => setForm({ ...form, email: value })} />
            <TextField label="Password" type="password" value={form.password} onChange={(value) => setForm({ ...form, password: value })} />
          </div>

          <button className="mt-6 w-full rounded-md bg-ink px-4 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60" disabled={loading}>
            {loading ? "Please wait..." : isSignup ? "Sign up" : "Log in"}
          </button>

          <p className="mt-5 text-center text-sm text-slate-500">
            {isSignup ? "Already have an account?" : "New to NutriTrack AI?"}{" "}
            <Link className="font-semibold text-mint" to={isSignup ? "/login" : "/signup"}>
              {isSignup ? "Log in" : "Create one"}
            </Link>
          </p>
        </form>
      </section>
    </main>
  );
}


function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <main className="min-h-screen bg-page text-ink">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col lg:flex-row">
        <aside className="border-b border-slate-200 bg-white px-4 py-4 lg:min-h-screen lg:w-64 lg:border-b-0 lg:border-r lg:px-5">
          <div className="flex items-center justify-between lg:block">
            <Link to="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-ink text-white">
                <Soup size={22} />
              </div>
              <div>
                <p className="text-lg font-bold">NutriTrack AI</p>
                <p className="text-xs text-slate-500">Smart nutrition log</p>
              </div>
            </Link>
            <button className="rounded-md p-2 text-slate-500 hover:bg-slate-100 lg:hidden" onClick={handleLogout} title="Logout">
              <LogOut size={20} />
            </button>
          </div>

          <nav className="mt-5 flex gap-2 overflow-x-auto lg:grid lg:overflow-visible">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    `flex shrink-0 items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold transition ${
                      isActive ? "bg-ink text-white" : "text-slate-600 hover:bg-slate-100"
                    }`
                  }
                >
                  <Icon size={18} />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>

          <div className="mt-8 hidden rounded-md bg-slate-50 p-4 lg:block">
            <p className="text-sm font-semibold">{user.name}</p>
            <p className="mt-1 break-all text-xs text-slate-500">{user.email}</p>
            <button className="mt-4 flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-ink" onClick={handleLogout}>
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </aside>

        <section className="flex-1 px-5 py-6 sm:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/meals" element={<MealLog />} />
            <Route path="/search" element={<FoodSearch />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </section>
      </div>
    </main>
  );
}


function Dashboard() {
  const { mealRefreshKey } = useAuth();
  const dashboardDate = todayISO();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, [mealRefreshKey]);

  async function loadDashboard() {
    setLoading(true);
    setError("");
    try {
      setData(await api.dashboard(dashboardDate));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <PageLoader />;
  if (error) return <ErrorState message={error} onRetry={loadDashboard} />;

  return (
    <Page title={`Hi, ${data.user.name}`} subtitle="Here is today's nutrition progress.">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MacroCard label="Calories" value={data.totals.calories} goal={data.goals.calories} suffix="kcal" color="bg-coral" />
        <MacroCard label="Protein" value={data.totals.protein} goal={data.goals.protein} suffix="g" color="bg-mint" />
        <MacroCard label="Carbs" value={data.totals.carbs} goal={data.goals.carbs} suffix="g" color="bg-sky-500" />
        <MacroCard label="Fat" value={data.totals.fat} goal={data.goals.fat} suffix="g" color="bg-amber-500" />
      </div>

      <div className="mt-6 grid gap-5 xl:grid-cols-[1fr_360px]">
        <Panel title="Today's meals" action={<Link className="text-sm font-semibold text-mint" to="/meals">Log meal</Link>}>
          <MealList meals={data.meals} compact />
        </Panel>
        <Panel title="Quick ideas">
          <div className="grid gap-3 text-sm text-slate-600">
            <p>Try logging meals like <strong>2 roti dal</strong>, <strong>150g paneer rice</strong>, or <strong>idli sambar</strong>.</p>
            <p>Your remaining calories today: <strong>{data.remaining.calories} kcal</strong>.</p>
            <p>Your remaining protein today: <strong>{data.remaining.protein} g</strong>.</p>
          </div>
        </Panel>
      </div>
    </Page>
  );
}


function MealLog() {
  const { notifyMealsChanged } = useAuth();
  const navigate = useNavigate();
  const [date, setDate] = useState(todayISO());
  const [description, setDescription] = useState("");
  const [mealType, setMealType] = useState("lunch");
  const [data, setData] = useState({ meals: [], totals: {} });
  const [estimate, setEstimate] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadMeals();
  }, [date]);

  async function loadMeals() {
    setLoading(true);
    setError("");
    try {
      setData(await api.meals(date));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function previewEstimate() {
    setSaving(true);
    setError("");
    try {
      const result = await api.estimate(description);
      setEstimate(result.estimate);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function addMeal(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.addMeal({
        description,
        meal_type: mealType,
        logged_at: `${date}T${new Date().toTimeString().slice(0, 8)}`,
      });
      setDescription("");
      setEstimate(null);
      await loadMeals();
      notifyMealsChanged();
      if (date === todayISO()) {
        navigate("/");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function deleteMeal(id) {
    setError("");
    try {
      await api.deleteMeal(id);
      await loadMeals();
      notifyMealsChanged();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <Page title="Meal logging" subtitle="Describe your meal and NutriTrack AI estimates the nutrition.">
      <div className="grid gap-5 xl:grid-cols-[420px_1fr]">
        <Panel title="Add a meal">
          {error && <Alert message={error} />}
          <form onSubmit={addMeal} className="mt-4 grid gap-4">
            <TextField label="Date" type="date" value={date} onChange={setDate} />
            <label className="grid gap-2 text-sm font-semibold text-slate-700">
              Meal type
              <select className="rounded-md border border-slate-200 bg-white px-3 py-3 outline-none focus:border-mint" value={mealType} onChange={(event) => setMealType(event.target.value)}>
                <option value="breakfast">Breakfast</option>
                <option value="lunch">Lunch</option>
                <option value="snack">Snack</option>
                <option value="dinner">Dinner</option>
              </select>
            </label>
            <label className="grid gap-2 text-sm font-semibold text-slate-700">
              Meal description
              <textarea className="min-h-28 rounded-md border border-slate-200 px-3 py-3 outline-none focus:border-mint" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Example: 2 roti dal and curd" />
            </label>
            <div className="flex flex-col gap-3 sm:flex-row">
              <button type="button" className="rounded-md border border-slate-200 px-4 py-3 font-semibold hover:bg-slate-50 disabled:opacity-60" onClick={previewEstimate} disabled={saving || !description}>
                Estimate
              </button>
              <button className="flex items-center justify-center gap-2 rounded-md bg-ink px-4 py-3 font-semibold text-white hover:bg-slate-800 disabled:opacity-60" disabled={saving || !description}>
                <Plus size={18} />
                Log meal
              </button>
            </div>
          </form>

          {estimate && (
            <div className="mt-5 rounded-md bg-slate-50 p-4">
              <p className="text-sm font-semibold">Estimate</p>
              <p className="mt-2 text-sm text-slate-600">{estimate.message}</p>
              <MacroRow totals={estimate.totals} />
            </div>
          )}
        </Panel>

        <Panel title={`Meals on ${date}`} action={<CalendarDays size={20} className="text-slate-400" />}>
          {loading ? <InlineLoader /> : <MealList meals={data.meals} onDelete={deleteMeal} />}
          {!loading && <MacroRow totals={data.totals} />}
        </Panel>
      </div>
    </Page>
  );
}


function FoodSearch() {
  const [query, setQuery] = useState("");
  const [foods, setFoods] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(loadFoods, 250);
    return () => clearTimeout(timer);
  }, [query]);

  async function loadFoods() {
    setLoading(true);
    setError("");
    try {
      const data = await api.foods(query);
      setFoods(data.foods);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Page title="Food search" subtitle="Browse the built-in Indian food database used by meal estimates.">
      <Panel>
        <TextField label="Search foods" value={query} onChange={setQuery} placeholder="Try paneer, dal, roti, idli, chole..." />
        {error && <Alert message={error} />}
        {loading ? (
          <InlineLoader />
        ) : (
          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {foods.map((food) => (
              <div key={food.name} className="rounded-md border border-slate-200 bg-white p-4">
                <h3 className="font-bold">{food.name}</h3>
                <p className="mt-1 text-sm text-slate-500">Serving: {food.serving_grams}g</p>
                <MacroRow totals={food.per_100g} label="Per 100g" />
              </div>
            ))}
            {foods.length === 0 && <EmptyState message="No foods found. Try a different search." />}
          </div>
        )}
      </Panel>
    </Page>
  );
}


function Analytics() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  async function loadAnalytics() {
    setLoading(true);
    setError("");
    try {
      setData(await api.weeklyAnalytics());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <PageLoader />;
  if (error) return <ErrorState message={error} onRetry={loadAnalytics} />;

  return (
    <Page title="Weekly analytics" subtitle="Review calories and protein for the last seven days.">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard label="Avg calories" value={`${data.averages.calories} kcal`} />
        <SummaryCard label="Avg protein" value={`${data.averages.protein} g`} />
        <SummaryCard label="Avg carbs" value={`${data.averages.carbs} g`} />
        <SummaryCard label="Avg fat" value={`${data.averages.fat} g`} />
      </div>

      <div className="mt-6 grid gap-5 xl:grid-cols-2">
        <Panel title="Calories">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.days}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="calories" fill="#ff6b5f" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Protein">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.days}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="protein" stroke="#2fbf71" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>
    </Page>
  );
}


function Profile() {
  const { user, setUser } = useAuth();
  const [form, setForm] = useState(user);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function saveProfile(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    try {
      const data = await api.updateProfile(form);
      setUser(data.user);
      setForm(data.user);
      setMessage("Profile updated.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Page title="Profile" subtitle="Set your goals and personal details for tracking.">
      <Panel title="Nutrition goals" action={<Settings size={20} className="text-slate-400" />}>
        {error && <Alert message={error} />}
        {message && <Success message={message} />}
        <form onSubmit={saveProfile} className="mt-5 grid gap-4 md:grid-cols-2">
          <TextField label="Name" value={form.name || ""} onChange={(value) => setForm({ ...form, name: value })} />
          <TextField label="Age" type="number" value={form.age || ""} onChange={(value) => setForm({ ...form, age: value })} />
          <TextField label="Height (cm)" type="number" value={form.height_cm || ""} onChange={(value) => setForm({ ...form, height_cm: value })} />
          <TextField label="Weight (kg)" type="number" value={form.weight_kg || ""} onChange={(value) => setForm({ ...form, weight_kg: value })} />
          <TextField label="Daily calories" type="number" value={form.calorie_goal || ""} onChange={(value) => setForm({ ...form, calorie_goal: value })} />
          <TextField label="Daily protein (g)" type="number" value={form.protein_goal || ""} onChange={(value) => setForm({ ...form, protein_goal: value })} />
          <TextField label="Daily carbs (g)" type="number" value={form.carbs_goal || ""} onChange={(value) => setForm({ ...form, carbs_goal: value })} />
          <TextField label="Daily fat (g)" type="number" value={form.fat_goal || ""} onChange={(value) => setForm({ ...form, fat_goal: value })} />
          <label className="grid gap-2 text-sm font-semibold text-slate-700 md:col-span-2">
            Activity level
            <select className="rounded-md border border-slate-200 bg-white px-3 py-3 outline-none focus:border-mint" value={form.activity_level || "moderate"} onChange={(event) => setForm({ ...form, activity_level: event.target.value })}>
              <option value="light">Light</option>
              <option value="moderate">Moderate</option>
              <option value="active">Active</option>
              <option value="athlete">Athlete</option>
            </select>
          </label>
          <button className="rounded-md bg-ink px-4 py-3 font-semibold text-white hover:bg-slate-800 disabled:opacity-60 md:col-span-2" disabled={saving}>
            {saving ? "Saving..." : "Save profile"}
          </button>
        </form>
      </Panel>
    </Page>
  );
}


function Page({ title, subtitle, children }) {
  return (
    <div>
      <header className="mb-6">
        <h1 className="text-3xl font-bold">{title}</h1>
        {subtitle && <p className="mt-2 text-slate-600">{subtitle}</p>}
      </header>
      {children}
    </div>
  );
}


function Panel({ title, action, children }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      {(title || action) && (
        <div className="mb-4 flex items-center justify-between gap-4">
          {title && <h2 className="text-lg font-bold">{title}</h2>}
          {action}
        </div>
      )}
      {children}
    </section>
  );
}


function MacroCard({ label, value, goal, suffix, color }) {
  const percent = Math.min(100, Math.round((Number(value || 0) / Number(goal || 1)) * 100));
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <div className="mt-3 flex items-end gap-2">
        <span className="text-3xl font-bold">{value}</span>
        <span className="pb-1 text-sm text-slate-500">/ {goal} {suffix}</span>
      </div>
      <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${percent}%` }} />
      </div>
      <p className="mt-2 text-xs text-slate-500">{percent}% of goal</p>
    </div>
  );
}


function SummaryCard({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
    </div>
  );
}


function MealList({ meals, onDelete, compact = false }) {
  if (!meals || meals.length === 0) {
    return <EmptyState message="No meals logged yet." />;
  }

  return (
    <div className="grid gap-3">
      {meals.map((meal) => (
        <div key={meal.id} className="flex flex-col gap-3 rounded-md border border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-semibold capitalize">{meal.description}</p>
            <p className="mt-1 text-sm text-slate-500">
              {meal.meal_type} • {new Date(meal.logged_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className={`grid gap-1 text-sm ${compact ? "" : "sm:grid-cols-4"}`}>
              <span>{meal.calories} kcal</span>
              <span>{meal.protein}g protein</span>
              {!compact && <span>{meal.carbs}g carbs</span>}
              {!compact && <span>{meal.fat}g fat</span>}
            </div>
            {onDelete && (
              <button className="rounded-md p-2 text-slate-500 hover:bg-white hover:text-coral" onClick={() => onDelete(meal.id)} title="Delete meal">
                <Trash2 size={18} />
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}


function MacroRow({ totals, label = "Totals" }) {
  if (!totals) return null;
  return (
    <div className="mt-4 grid gap-2 rounded-md bg-white p-3 text-sm sm:grid-cols-5">
      <strong>{label}</strong>
      <span>{totals.calories || 0} kcal</span>
      <span>{totals.protein || 0}g protein</span>
      <span>{totals.carbs || 0}g carbs</span>
      <span>{totals.fat || 0}g fat</span>
    </div>
  );
}


function TextField({ label, value, onChange, type = "text", placeholder = "" }) {
  return (
    <label className="grid gap-2 text-sm font-semibold text-slate-700">
      {label}
      <input
        className="rounded-md border border-slate-200 px-3 py-3 outline-none transition focus:border-mint"
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}


function Alert({ message }) {
  return <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">{message}</div>;
}


function Success({ message }) {
  return <div className="mt-4 rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm font-medium text-green-700">{message}</div>;
}


function EmptyState({ message }) {
  return <div className="rounded-md border border-dashed border-slate-200 bg-slate-50 p-5 text-center text-sm text-slate-500">{message}</div>;
}


function InlineLoader() {
  return <div className="rounded-md bg-slate-50 p-5 text-sm font-semibold text-slate-500">Loading...</div>;
}


function PageLoader() {
  return <InlineLoader />;
}


function FullPageLoader({ label }) {
  return <main className="grid min-h-screen place-items-center bg-page text-sm font-semibold text-slate-500">{label}</main>;
}


function ErrorState({ message, onRetry }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-5">
      <p className="font-semibold text-red-700">{message}</p>
      <button className="mt-4 rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white" onClick={onRetry}>
        Try again
      </button>
    </div>
  );
}


export default App;
