<template>
  <div class="admin-root">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="https://www.glaido.com/images/glaido-main-white.svg" alt="SpecFlow" class="logo-img" />
        <span class="admin-badge">ADMIN</span>
      </div>
      <nav class="sidebar-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="nav-item"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span class="nav-icon" v-html="tab.icon"></span>
          <span>{{ tab.label }}</span>
        </button>
      </nav>
      <div class="sidebar-footer">
        <div class="admin-profile">
          <div class="avatar">{{ authStore.user?.name?.[0]?.toUpperCase() || 'A' }}</div>
          <div class="profile-info">
            <div class="profile-name">{{ authStore.user?.name || 'Admin' }}</div>
            <div class="profile-role">Super Admin</div>
          </div>
        </div>
        <router-link to="/dashboard" class="back-btn">← App</router-link>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="top-header">
        <div>
          <h1 class="page-title">{{ currentTab?.label }}</h1>
          <p class="page-sub">{{ currentTab?.description }}</p>
        </div>
        <div class="header-right">
          <div class="last-updated">Last updated: {{ lastUpdated }}</div>
          <button class="refresh-btn" @click="loadAll" :disabled="loading">
            <span :class="{ spinning: loading }">↻</span> Refresh
          </button>
        </div>
      </header>

      <!-- Loading overlay -->
      <div v-if="loading && !stats" class="loading-overlay">
        <div class="loader-ring"></div>
        <p>Loading analytics…</p>
      </div>

      <!-- ===== OVERVIEW TAB ===== -->
      <div v-if="activeTab === 'overview' && stats" class="tab-content">
        <!-- KPI Cards Row 1 -->
        <div class="kpi-grid">
          <div class="kpi-card kpi-blue">
            <div class="kpi-icon">👥</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ stats.users.total.toLocaleString() }}</div>
              <div class="kpi-label">Registered Users</div>
              <div class="kpi-delta positive">+{{ stats.users.new_7d }} this week</div>
            </div>
          </div>
          <div class="kpi-card kpi-green">
            <div class="kpi-icon">📄</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ stats.specs.total.toLocaleString() }}</div>
              <div class="kpi-label">Specs Uploaded</div>
              <div class="kpi-delta positive">+{{ stats.specs.new_7d }} this week</div>
            </div>
          </div>
          <div class="kpi-card kpi-yellow">
            <div class="kpi-icon">🗺️</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ stats.journeys.total.toLocaleString() }}</div>
              <div class="kpi-label">Journeys Created</div>
              <div class="kpi-delta neutral">{{ stats.journeys.ai_generated }} AI / {{ stats.journeys.manual }} Manual</div>
            </div>
          </div>
          <div class="kpi-card" :class="stats.executions.success_rate >= 80 ? 'kpi-green' : stats.executions.success_rate >= 50 ? 'kpi-yellow' : 'kpi-red'">
            <div class="kpi-icon">⚡</div>
            <div class="kpi-body">
              <div class="kpi-value">{{ stats.executions.success_rate }}%</div>
              <div class="kpi-label">Execution Success Rate</div>
              <div class="kpi-delta" :class="stats.executions.success_rate >= 80 ? 'positive' : 'negative'">
                {{ stats.executions.total }} total runs
              </div>
            </div>
          </div>
        </div>

        <!-- Execution Breakdown -->
        <div class="section-row">
          <div class="card exec-status-card">
            <h3 class="card-title">Execution Status Breakdown</h3>
            <div class="status-bars">
              <div class="status-bar-row">
                <span class="status-label">✅ Successful</span>
                <div class="bar-track">
                  <div class="bar-fill bar-green" :style="{ width: execSuccessWidth + '%' }"></div>
                </div>
                <span class="status-count green-text">{{ stats.executions.successful }}</span>
              </div>
              <div class="status-bar-row">
                <span class="status-label">❌ Failed</span>
                <div class="bar-track">
                  <div class="bar-fill bar-red" :style="{ width: execFailWidth + '%' }"></div>
                </div>
                <span class="status-count red-text">{{ stats.executions.failed }}</span>
              </div>
              <div class="status-bar-row">
                <span class="status-label">⏳ Running</span>
                <div class="bar-track">
                  <div class="bar-fill bar-yellow" :style="{ width: execRunWidth + '%' }"></div>
                </div>
                <span class="status-count yellow-text">{{ stats.executions.running }}</span>
              </div>
            </div>
          </div>

          <div class="card plan-donut-card">
            <h3 class="card-title">Users by Plan</h3>
            <div class="donut-wrap">
              <canvas id="planDonutChart" width="200" height="200"></canvas>
            </div>
            <div class="plan-legend">
              <div v-for="(plan, idx) in planLegend" :key="plan.name" class="legend-row">
                <span class="legend-dot" :style="{ background: plan.color }"></span>
                <span class="legend-name">{{ plan.name }}</span>
                <span class="legend-val">{{ plan.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Growth Charts -->
        <div class="card chart-card">
          <div class="chart-header">
            <h3 class="card-title">User Growth</h3>
            <div class="time-tabs">
              <button v-for="d in [7,14,30]" :key="d" class="time-btn" :class="{ active: growthDays === d }" @click="setGrowthDays(d)">{{ d }}d</button>
            </div>
          </div>
          <canvas id="userGrowthChart" height="80"></canvas>
        </div>

        <div class="two-col-charts">
          <div class="card chart-card">
            <h3 class="card-title">Spec Uploads Over Time</h3>
            <canvas id="specChart" height="100"></canvas>
          </div>
          <div class="card chart-card">
            <h3 class="card-title">Execution Results Over Time</h3>
            <canvas id="execChart" height="100"></canvas>
          </div>
        </div>
      </div>

      <!-- ===== USERS TAB ===== -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <div class="users-toolbar">
          <div class="plan-filters">
            <button v-for="p in ['all','free','starter','team','pro']" :key="p"
              class="plan-filter-btn" :class="{ active: userPlanFilter === p }"
              @click="setUserFilter(p)">
              {{ p.charAt(0).toUpperCase() + p.slice(1) }}
            </button>
          </div>
          <button class="primary-btn" @click="showAdminModal = true">+ Create Admin</button>
        </div>

        <div class="card table-card">
          <table class="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Plan</th>
                <th>Admin</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>
                  <div class="user-cell">
                    <div class="user-avatar">{{ u.name?.[0]?.toUpperCase() || '?' }}</div>
                    {{ u.name || '—' }}
                  </div>
                </td>
                <td class="muted">{{ u.email }}</td>
                <td><span class="plan-badge" :class="'badge-' + u.plan">{{ u.plan }}</span></td>
                <td>
                  <span v-if="u.is_admin" class="admin-chip">Admin</span>
                  <span v-else class="muted">—</span>
                </td>
                <td class="muted">{{ formatDate(u.created_at) }}</td>
              </tr>
              <tr v-if="users.length === 0">
                <td colspan="5" class="empty-row">No users found.</td>
              </tr>
            </tbody>
          </table>
          <div class="pagination">
            <button class="page-btn" :disabled="userPage <= 1" @click="userPage--;loadUsers()">← Prev</button>
            <span class="page-info">Page {{ userPage }}</span>
            <button class="page-btn" :disabled="users.length < 20" @click="userPage++;loadUsers()">Next →</button>
          </div>
        </div>
      </div>

      <!-- ===== ACTIVITY TAB ===== -->
      <div v-if="activeTab === 'activity'" class="tab-content">
        <div class="card table-card">
          <h3 class="card-title">Recent Execution Activity</h3>
          <table class="data-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Journey</th>
                <th>User</th>
                <th>Started</th>
                <th>Completed</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in activity" :key="a.execution_id">
                <td>
                  <span class="status-chip" :class="'chip-' + a.status">
                    {{ a.status === 'completed' ? '✅ Success' : a.status === 'failed' ? '❌ Failed' : '⏳ Running' }}
                  </span>
                </td>
                <td>{{ a.journey_name }}</td>
                <td>
                  <div class="user-cell">
                    <div class="user-avatar sm">{{ a.user_name?.[0]?.toUpperCase() || '?' }}</div>
                    <span>{{ a.user_name }}<br/><small class="muted">{{ a.user_email }}</small></span>
                  </div>
                </td>
                <td class="muted">{{ formatDateTime(a.started_at) }}</td>
                <td class="muted">{{ a.completed_at ? formatDateTime(a.completed_at) : '—' }}</td>
              </tr>
              <tr v-if="activity.length === 0">
                <td colspan="5" class="empty-row">No recent activity.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- Create Admin Modal -->
    <Transition name="modal">
      <div v-if="showAdminModal" class="modal-overlay" @click.self="showAdminModal = false">
        <div class="modal-box">
          <h2 class="modal-title">Create Admin Account</h2>
          <p class="modal-sub">New admin will have full dashboard access and pro plan.</p>
          <form @submit.prevent="createAdmin" class="admin-form">
            <div class="form-group">
              <label>Full Name</label>
              <input v-model="newAdmin.name" type="text" placeholder="Jane Smith" required />
            </div>
            <div class="form-group">
              <label>Email Address</label>
              <input v-model="newAdmin.email" type="email" placeholder="admin@example.com" required />
            </div>
            <div class="form-group">
              <label>Password</label>
              <input v-model="newAdmin.password" type="password" placeholder="Min. 8 characters" required minlength="8" />
            </div>
            <div v-if="adminFormError" class="form-error">{{ adminFormError }}</div>
            <div v-if="adminFormSuccess" class="form-success">{{ adminFormSuccess }}</div>
            <div class="modal-actions">
              <button type="button" class="secondary-btn" @click="showAdminModal = false">Cancel</button>
              <button type="submit" class="primary-btn" :disabled="creatingAdmin">
                {{ creatingAdmin ? 'Creating…' : 'Create Admin' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'

const authStore = useAuthStore()

// ── Tabs ──────────────────────────────────────────────────────────
const tabs = [
  { id: 'overview', label: 'Overview', description: 'Platform-wide analytics and growth metrics', icon: '📊' },
  { id: 'users',    label: 'Users',    description: 'Registered users and plan distribution',     icon: '👥' },
  { id: 'activity', label: 'Activity', description: 'Recent execution and journey activity',       icon: '⚡' },
]
const activeTab = ref('overview')
const currentTab = computed(() => tabs.find(t => t.id === activeTab.value))

// ── State ─────────────────────────────────────────────────────────
const loading     = ref(false)
const stats       = ref(null)
const growth      = ref(null)
const users       = ref([])
const activity    = ref([])
const growthDays  = ref(30)
const userPage    = ref(1)
const userPlanFilter = ref('all')
const lastUpdated = ref('—')

// Chart instances
let planChart = null
let userGrowthChartInst = null
let specChartInst = null
let execChartInst = null

// Modal
const showAdminModal  = ref(false)
const creatingAdmin   = ref(false)
const adminFormError  = ref('')
const adminFormSuccess = ref('')
const newAdmin = ref({ name: '', email: '', password: '' })

// ── Data Loaders ──────────────────────────────────────────────────
async function loadAll() {
  loading.value = true
  try {
    await Promise.all([loadStats(), loadGrowth(), loadUsers(), loadActivity()])
    lastUpdated.value = new Date().toLocaleTimeString()
    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  const { data } = await apiClient.get('/api/admin/stats')
  stats.value = data
}

async function loadGrowth() {
  const { data } = await apiClient.get(`/api/admin/growth?days=${growthDays.value}`)
  growth.value = data
}

async function loadUsers() {
  const plan = userPlanFilter.value === 'all' ? '' : `&plan=${userPlanFilter.value}`
  const { data } = await apiClient.get(`/api/admin/users?page=${userPage.value}&limit=20${plan}`)
  users.value = data
}

async function loadActivity() {
  const { data } = await apiClient.get('/api/admin/recent-activity?limit=15')
  activity.value = data
}

async function setGrowthDays(d) {
  growthDays.value = d
  await loadGrowth()
  await nextTick()
  renderGrowthCharts()
}

async function setUserFilter(p) {
  userPlanFilter.value = p
  userPage.value = 1
  await loadUsers()
}

// ── Admin Creation ─────────────────────────────────────────────────
async function createAdmin() {
  creatingAdmin.value = true
  adminFormError.value = ''
  adminFormSuccess.value = ''
  try {
    await apiClient.post('/api/admin/create-admin', {
      name: newAdmin.value.name,
      email: newAdmin.value.email,
      password: newAdmin.value.password,
      is_admin: true,
    })
    adminFormSuccess.value = `Admin account for ${newAdmin.value.email} created!`
    newAdmin.value = { name: '', email: '', password: '' }
    await loadUsers()
  } catch (e) {
    adminFormError.value = e.response?.data?.detail || 'Failed to create admin'
  } finally {
    creatingAdmin.value = false
  }
}

// ── Computed ──────────────────────────────────────────────────────
const execSuccessWidth = computed(() => {
  if (!stats.value || stats.value.executions.total === 0) return 0
  return (stats.value.executions.successful / stats.value.executions.total) * 100
})
const execFailWidth = computed(() => {
  if (!stats.value || stats.value.executions.total === 0) return 0
  return (stats.value.executions.failed / stats.value.executions.total) * 100
})
const execRunWidth = computed(() => {
  if (!stats.value || stats.value.executions.total === 0) return 0
  return (stats.value.executions.running / stats.value.executions.total) * 100
})

const planColors = { free: '#99A1AF', starter: '#60A5FA', team: '#BFF549', pro: '#a78bfa' }
const planLegend = computed(() => {
  if (!stats.value) return []
  return Object.entries(stats.value.users.by_plan).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
    color: planColors[name] || '#888',
  }))
})

// ── Charts ────────────────────────────────────────────────────────
function destroyChart(inst) { if (inst) { inst.destroy() } }

async function loadChartJs() {
  if (window.Chart) return
  await new Promise((res, rej) => {
    const s = document.createElement('script')
    s.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js'
    s.onload = res; s.onerror = rej
    document.head.appendChild(s)
  })
}

async function renderCharts() {
  await loadChartJs()
  renderDonutChart()
  renderGrowthCharts()
}

function renderDonutChart() {
  if (!stats.value) return
  const ctx = document.getElementById('planDonutChart')
  if (!ctx) return
  destroyChart(planChart)
  const plans = stats.value.users.by_plan
  planChart = new window.Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: Object.keys(plans).map(p => p.charAt(0).toUpperCase() + p.slice(1)),
      datasets: [{
        data: Object.values(plans),
        backgroundColor: Object.keys(plans).map(p => planColors[p] || '#888'),
        borderColor: '#111',
        borderWidth: 3,
        hoverOffset: 8,
      }]
    },
    options: {
      cutout: '68%',
      plugins: { legend: { display: false } },
      animation: { animateScale: true, duration: 600 }
    }
  })
}

function renderGrowthCharts() {
  if (!growth.value) return

  const labels = growth.value.labels.map(d => {
    const dt = new Date(d)
    return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })

  const gridColor  = 'rgba(255,255,255,0.06)'
  const textColor  = '#99A1AF'
  const baseOpts = {
    responsive: true,
    plugins: { legend: { labels: { color: textColor, font: { family: 'Inter' } } } },
    scales: {
      x: { ticks: { color: textColor, maxTicksLimit: 8, font: { family: 'Inter', size: 11 } }, grid: { color: gridColor } },
      y: { ticks: { color: textColor, font: { family: 'Inter', size: 11 } }, grid: { color: gridColor }, beginAtZero: true }
    },
    animation: { duration: 500 }
  }

  // User growth chart
  const ugCtx = document.getElementById('userGrowthChart')
  if (ugCtx) {
    destroyChart(userGrowthChartInst)
    userGrowthChartInst = new window.Chart(ugCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'New Users',
          data: growth.value.users,
          borderColor: '#BFF549',
          backgroundColor: 'rgba(191,245,73,0.10)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#BFF549',
          pointRadius: 3,
        }]
      },
      options: baseOpts
    })
  }

  // Spec chart
  const spCtx = document.getElementById('specChart')
  if (spCtx) {
    destroyChart(specChartInst)
    specChartInst = new window.Chart(spCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Specs Uploaded',
          data: growth.value.specs,
          backgroundColor: 'rgba(96,165,250,0.7)',
          borderColor: '#60A5FA',
          borderRadius: 4,
        }]
      },
      options: baseOpts
    })
  }

  // Execution chart
  const exCtx = document.getElementById('execChart')
  if (exCtx) {
    destroyChart(execChartInst)
    execChartInst = new window.Chart(exCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Successful',
            data: growth.value.executions_successful,
            borderColor: '#4ade80',
            backgroundColor: 'rgba(74,222,128,0.10)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#4ade80',
            pointRadius: 3,
          },
          {
            label: 'Failed',
            data: growth.value.executions_failed,
            borderColor: '#f87171',
            backgroundColor: 'rgba(248,113,113,0.10)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#f87171',
            pointRadius: 3,
          }
        ]
      },
      options: baseOpts
    })
  }
}

// ── Helpers ───────────────────────────────────────────────────────
function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
function formatDateTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// Re-render charts when switching to overview
watch(activeTab, async (val) => {
  if (val === 'overview' && stats.value) {
    await nextTick()
    renderCharts()
  }
})

onMounted(loadAll)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root layout ── */
.admin-root {
  display: flex;
  height: 100vh;
  background: #050505;
  color: #e8e8e8;
  font-family: 'Inter', system-ui, sans-serif;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: 240px;
  min-width: 240px;
  background: #0a0a0a;
  border-right: 1px solid rgba(255,255,255,0.07);
  display: flex;
  flex-direction: column;
  padding: 0;
}

.sidebar-logo {
  padding: 24px 20px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.logo-img { height: 26px; }
.admin-badge {
  background: #BFF549;
  color: #000;
  font-size: 9px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 99px;
  letter-spacing: 0.08em;
}

.sidebar-nav {
  padding: 16px 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: #888;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s ease;
  width: 100%;
  text-align: left;
}
.nav-item:hover { background: rgba(255,255,255,0.05); color: #e8e8e8; }
.nav-item.active { background: rgba(191,245,73,0.12); color: #BFF549; }
.nav-icon { font-size: 16px; }

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.admin-profile { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #BFF549, #82b800);
  color: #000;
  font-weight: 700;
  font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.profile-name { font-size: 13px; font-weight: 600; color: #e8e8e8; }
.profile-role { font-size: 11px; color: #BFF549; }
.back-btn {
  font-size: 12px;
  color: #888;
  text-decoration: none;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.1);
  text-align: center;
  transition: all 0.15s;
}
.back-btn:hover { color: #BFF549; border-color: #BFF549; }

/* ── Main ── */
.main-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.main-content::-webkit-scrollbar { width: 6px; }
.main-content::-webkit-scrollbar-track { background: transparent; }
.main-content::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 3px; }

/* ── Header ── */
.top-header {
  padding: 28px 32px 20px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  position: sticky;
  top: 0;
  background: rgba(5,5,5,0.95);
  backdrop-filter: blur(12px);
  z-index: 10;
}
.page-title { font-size: 22px; font-weight: 700; color: #fff; margin: 0 0 4px; }
.page-sub { font-size: 13px; color: #666; margin: 0; }
.header-right { display: flex; align-items: center; gap: 14px; }
.last-updated { font-size: 12px; color: #555; }
.refresh-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: #ccc;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.refresh-btn:hover:not(:disabled) { background: rgba(191,245,73,0.1); border-color: #BFF549; color: #BFF549; }
.refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.spinning { display: inline-block; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Loading ── */
.loading-overlay {
  flex: 1;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 20px; color: #666;
}
.loader-ring {
  width: 48px; height: 48px;
  border: 3px solid rgba(191,245,73,0.2);
  border-top-color: #BFF549;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ── Tab Content ── */
.tab-content {
  padding: 28px 32px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── KPI Grid ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.kpi-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px 20px;
  border-radius: 14px;
  background: #0f0f0f;
  border: 1px solid rgba(255,255,255,0.07);
  transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.4); }
.kpi-blue  { border-left: 3px solid #60A5FA; }
.kpi-green { border-left: 3px solid #4ade80; }
.kpi-yellow{ border-left: 3px solid #fbbf24; }
.kpi-red   { border-left: 3px solid #f87171; }
.kpi-icon  { font-size: 28px; }
.kpi-value { font-size: 28px; font-weight: 800; color: #fff; line-height: 1; }
.kpi-label { font-size: 12px; color: #888; margin: 4px 0; }
.kpi-delta { font-size: 12px; font-weight: 500; }
.kpi-delta.positive { color: #4ade80; }
.kpi-delta.negative { color: #f87171; }
.kpi-delta.neutral  { color: #99A1AF; }

/* ── Cards ── */
.card {
  background: #0f0f0f;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 24px;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0 0 20px;
}

/* ── Section row ── */
.section-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

/* ── Exec Status Bars ── */
.status-bars { display: flex; flex-direction: column; gap: 16px; }
.status-bar-row { display: flex; align-items: center; gap: 12px; }
.status-label { width: 110px; font-size: 13px; color: #aaa; flex-shrink: 0; }
.bar-track {
  flex: 1;
  height: 10px;
  background: rgba(255,255,255,0.06);
  border-radius: 99px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.8s cubic-bezier(.4,0,.2,1);
}
.bar-green  { background: linear-gradient(90deg, #22c55e, #4ade80); box-shadow: 0 0 10px rgba(74,222,128,0.4); }
.bar-red    { background: linear-gradient(90deg, #dc2626, #f87171); box-shadow: 0 0 10px rgba(248,113,113,0.4); }
.bar-yellow { background: linear-gradient(90deg, #d97706, #fbbf24); box-shadow: 0 0 10px rgba(251,191,36,0.4); }
.status-count { width: 40px; font-size: 13px; font-weight: 600; text-align: right; }
.green-text  { color: #4ade80; }
.red-text    { color: #f87171; }
.yellow-text { color: #fbbf24; }

/* ── Donut ── */
.plan-donut-card { display: flex; flex-direction: column; }
.donut-wrap { display: flex; justify-content: center; margin-bottom: 16px; }
.plan-legend { display: flex; flex-direction: column; gap: 8px; }
.legend-row { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-name { flex: 1; color: #aaa; }
.legend-val { font-weight: 600; color: #e8e8e8; }

/* ── Charts ── */
.chart-card { padding: 24px; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.chart-header .card-title { margin: 0; }
.time-tabs { display: flex; gap: 6px; }
.time-btn {
  padding: 5px 12px;
  font-size: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  color: #888;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}
.time-btn.active, .time-btn:hover { background: rgba(191,245,73,0.12); border-color: #BFF549; color: #BFF549; }
.two-col-charts { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

/* ── Users tab ── */
.users-toolbar { display: flex; justify-content: space-between; align-items: center; }
.plan-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.plan-filter-btn {
  padding: 6px 14px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px;
  color: #888;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.plan-filter-btn.active, .plan-filter-btn:hover { background: rgba(191,245,73,0.12); border-color: #BFF549; color: #BFF549; }

/* ── Table ── */
.table-card { padding: 0; overflow: hidden; }
.table-card .card-title { padding: 20px 24px 0; }
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.02);
}
.data-table td {
  padding: 13px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: #ccc;
  vertical-align: middle;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: rgba(255,255,255,0.025); }
.muted { color: #666 !important; }
.user-cell { display: flex; align-items: center; gap: 10px; }
.user-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #BFF549, #82b800);
  color: #000;
  font-size: 12px;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.user-avatar.sm { width: 24px; height: 24px; font-size: 10px; }
.empty-row { text-align: center; color: #444; padding: 32px !important; }

/* ── Badges / Chips ── */
.plan-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}
.badge-free    { background: rgba(153,161,175,0.15); color: #99A1AF; }
.badge-starter { background: rgba(96,165,250,0.15);  color: #60A5FA; }
.badge-team    { background: rgba(191,245,73,0.15);  color: #BFF549; }
.badge-pro     { background: rgba(167,139,250,0.15); color: #a78bfa; }

.admin-chip {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(191,245,73,0.15);
  color: #BFF549;
}

.status-chip {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 500;
}
.chip-completed { background: rgba(74,222,128,0.12); color: #4ade80; }
.chip-failed    { background: rgba(248,113,113,0.12); color: #f87171; }
.chip-running   { background: rgba(251,191,36,0.12); color: #fbbf24; }

/* ── Pagination ── */
.pagination {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid rgba(255,255,255,0.06);
  justify-content: flex-end;
}
.page-btn {
  padding: 6px 14px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  color: #aaa;
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.page-btn:hover:not(:disabled) { border-color: #BFF549; color: #BFF549; }
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.page-info { font-size: 12px; color: #555; }

/* ── Buttons ── */
.primary-btn {
  padding: 9px 20px;
  background: #BFF549;
  color: #000;
  border: none;
  border-radius: 99px;
  font-size: 13px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 0 40px -10px rgba(191,245,73,0.5);
}
.primary-btn:hover:not(:disabled) { background: #d4ff55; box-shadow: 0 0 50px -8px rgba(191,245,73,0.7); }
.primary-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.secondary-btn {
  padding: 9px 20px;
  background: rgba(255,255,255,0.06);
  color: #ccc;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 99px;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.secondary-btn:hover { border-color: #BFF549; color: #BFF549; }

/* ── Modal ── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: #121212;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 18px;
  padding: 36px;
  width: 440px;
  max-width: 95vw;
  box-shadow: 0 30px 80px rgba(0,0,0,0.6);
}
.modal-title { font-size: 20px; font-weight: 700; color: #fff; margin: 0 0 6px; }
.modal-sub { font-size: 13px; color: #666; margin: 0 0 28px; }
.admin-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.06em; }
.form-group input {
  padding: 11px 14px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}
.form-group input:focus { border-color: #BFF549; background: rgba(191,245,73,0.04); }
.form-error { font-size: 13px; color: #f87171; background: rgba(248,113,113,0.1); padding: 10px 14px; border-radius: 8px; }
.form-success { font-size: 13px; color: #4ade80; background: rgba(74,222,128,0.1); padding: 10px 14px; border-radius: 8px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px; }

/* ── Modal transition ── */
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }
</style>
