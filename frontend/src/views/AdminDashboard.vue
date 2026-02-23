<template>
  <div class="admin-wrapper" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- Left Sidebar -->
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <RouterLink to="/" class="flex items-center space-x-2 group pl-2">
          <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center transform rotate-12 group-hover:rotate-0 transition-transform">
            <Zap :size="20" class="text-black fill-current" />
          </div>
          <span class="text-xl font-black tracking-tighter text-white" v-if="!sidebarCollapsed">
            Spec<span class="text-primary">Flow</span>
            <span class="admin-label">ADMIN</span>
          </span>
        </RouterLink>
      </div>

      <nav class="sidebar-content">
        <div class="nav-section" v-if="!sidebarCollapsed">Dashboard</div>
        <button
          v-for="tab in tabs.slice(0, 3)"
          :key="tab.id"
          class="nav-link"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" :size="20" class="nav-icon" />
          <span v-if="!sidebarCollapsed">{{ tab.label }}</span>
          <div v-show="activeTab === tab.id" class="active-indicator"></div>
        </button>

        <div class="nav-divider"></div>
        <div class="nav-section" v-if="!sidebarCollapsed">Platform</div>
        <button
          v-for="tab in tabs.slice(3)"
          :key="tab.id"
          class="nav-link"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" :size="20" class="nav-icon" />
          <span v-if="!sidebarCollapsed">{{ tab.label }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <div class="user-profile-summary" v-if="!sidebarCollapsed">
          <div class="avatar-ring">
            <div class="avatar-inner">{{ authStore.user?.name?.[0]?.toUpperCase() }}</div>
            <div class="status-dot"></div>
          </div>
          <div class="user-details">
            <div class="user-name">{{ authStore.user?.name }}</div>
            <div class="user-role">Super Admin</div>
          </div>
        </div>
        <button @click="sidebarCollapsed = !sidebarCollapsed" class="collapse-toggle" :class="{ 'is-collapsed': sidebarCollapsed }">
          <ChevronLeft v-if="!sidebarCollapsed" :size="20" />
          <ChevronRight v-else :size="20" />
          <span v-if="!sidebarCollapsed" class="ml-2">Collapse</span>
        </button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="admin-main">
      <!-- Sticky Top Header -->
      <header class="admin-header">
        <div class="header-search">
          <Search :size="18" class="search-icon" />
          <input type="text" placeholder="Search analytics, users..." v-model="searchQuery" />
        </div>

        <div class="header-actions">
          <div class="action-icons">
            <button class="icon-btn" title="Refresh Data" @click="loadAll" :disabled="loading">
              <RefreshCw :size="20" :class="{ spinning: loading }" />
            </button>
            <button class="icon-btn" title="Notifications">
              <Bell :size="20" />
              <div class="notification-badge"></div>
            </button>
            <button class="icon-btn" title="Redirect to App" @click="router.push('/dashboard')">
              <LayoutDashboard :size="20" />
            </button>
          </div>
          <div class="user-dropdown" @click="activeTab = 'settings'">
            <div class="dropdown-trigger">
              <div class="user-info text-right mr-3 hidden sm:block">
                <div class="text-sm font-bold text-white">{{ authStore.user?.name }}</div>
                <div class="text-[10px] text-primary/80 font-black tracking-widest uppercase">Online</div>
              </div>
              <div class="mini-avatar">{{ authStore.user?.name?.[0]?.toUpperCase() }}</div>
              <Settings :size="16" class="ml-2 text-gray-500 cursor-pointer hover:text-primary transition-colors" />
            </div>
          </div>
        </div>
      </header>

      <!-- Dashboard View -->
      <div class="admin-container scrollbar-hide">
        <!-- Page Title & Refresh Info -->
        <div class="container-header">
          <div class="title-group">
            <h2>{{ currentTab?.label }}</h2>
            <p>{{ currentTab?.description }}</p>
          </div>
          <div class="time-group">
            <span class="last-sync">Last updated: {{ lastUpdated }}</span>
          </div>
        </div>

        <!-- Overview Content -->
        <template v-if="activeTab === 'overview' && stats">
          <!-- KPI Cards Row -->
          <div class="kpi-row">
            <div class="orbit-card kpi-widget purple">
              <div class="widget-header">
                <div class="widget-title">
                  <div class="icon-box"><Users :size="18" /></div>
                  Users
                </div>
                <div class="trend positive">+{{ stats.users.new_7d }}%</div>
              </div>
              <div class="widget-value-group">
                <div class="widget-value">{{ stats.users.total.toLocaleString() }}</div>
                <div class="widget-sub-label">Total Records</div>
              </div>
              <div class="widget-footer">Active Accounts</div>
              <div class="widget-spark">
                <canvas id="sparkUsers"></canvas>
              </div>
            </div>

            <div class="orbit-card kpi-widget cyan">
              <div class="widget-header">
                <div class="widget-title">
                  <div class="icon-box"><FileCode2 :size="18" /></div>
                  Specs
                </div>
                <div class="trend positive">+{{ stats.specs.new_7d }}%</div>
              </div>
              <div class="widget-value-group">
                <div class="widget-value">{{ stats.specs.total.toLocaleString() }}</div>
                <div class="widget-sub-label">Active Definitions</div>
              </div>
              <div class="widget-footer">Validated OpenAPI</div>
              <div class="widget-spark">
                <canvas id="sparkSpecs"></canvas>
              </div>
            </div>

            <div class="orbit-card kpi-widget lime">
              <div class="widget-header">
                <div class="widget-title">
                  <div class="icon-box"><Map :size="18" /></div>
                  AI Journeys
                </div>
                <div class="trend positive">+{{ stats.journeys.total ? Math.round((stats.journeys.ai_generated / stats.journeys.total) * 100) : 0 }}%</div>
              </div>
              <div class="widget-value-group">
                <div class="widget-value">{{ stats.journeys.ai_generated.toLocaleString() }}</div>
                <div class="widget-sub-label">Neural Insights</div>
              </div>
              <div class="widget-footer">AI Generated Paths</div>
              <div class="widget-spark">
                <canvas id="sparkJourneys"></canvas>
              </div>
            </div>

            <div class="orbit-card kpi-widget cyan">
              <div class="widget-header">
                <div class="widget-title">
                  <div class="icon-box"><Activity :size="18" /></div>
                  Manual Journeys
                </div>
                <div class="trend positive">{{ stats.journeys.manual.toLocaleString() }}</div>
              </div>
              <div class="widget-value-group">
                <div class="widget-value">{{ stats.journeys.manual.toLocaleString() }}</div>
                <div class="widget-sub-label">Curated Flows</div>
              </div>
              <div class="widget-footer">Manually Designed</div>
              <div class="widget-spark">
                <canvas id="sparkManual"></canvas>
              </div>
            </div>

            <div class="orbit-card kpi-widget indigo">
              <div class="widget-header">
                <div class="widget-title">
                  <div class="icon-box"><Activity :size="18" /></div>
                  Execution Success Rate
                </div>
                <div class="trend" :class="stats.executions.success_rate >= 80 ? 'positive' : 'negative'" title="Performance Trend">
                  {{ stats.executions.success_rate }}% Stability
                </div>
              </div>
              <div class="widget-value-group">
                <div class="widget-value">{{ stats.executions.success_rate }}%</div>
                <div class="widget-sub-label">Pass Rate</div>
              </div>
              <div class="widget-footer">
                <span class="text-green-400 font-bold">{{ stats.executions.successful }}</span> Passed / 
                <span class="text-red-400 font-bold">{{ stats.executions.failed }}</span> Failed
              </div>
              <div class="widget-spark">
                <canvas id="sparkSuccess"></canvas>
              </div>
            </div>
          </div>

          <!-- Main Grid (Charts) -->
          <div class="dashboard-grid">
            <div class="orbit-card main-chart-card">
              <div class="card-header">
                <h3>User Growth Rate</h3>
                <div class="chart-labels">
                  <span class="legend-item"><div class="dot lime"></div> Current</span>
                  <span class="legend-item"><div class="dot gray"></div> Previous</span>
                </div>
                <select class="period-select" @change="e => setGrowthDays(parseInt(e.target.value))">
                  <option value="7">7 Days</option>
                  <option value="30" selected>30 Days</option>
                  <option value="90">90 Days</option>
                </select>
              </div>
              <div class="chart-content">
                <canvas id="userGrowthChart"></canvas>
              </div>
            </div>

            <div class="orbit-card side-chart-card">
              <div class="card-header">
                <h3>Plan Distribution</h3>
                <button class="more-btn"><MoreVertical :size="16" /></button>
              </div>
              <div class="donut-content">
                <canvas id="planDonutChart"></canvas>
                <div class="donut-center">
                  <div class="total-val">{{ stats.users.total }}</div>
                  <div class="total-label">Subscribers</div>
                </div>
              </div>
              <div class="plan-list">
                <div v-for="plan in planLegend" :key="plan.name" class="plan-item">
                  <div class="plan-info">
                    <div class="plan-dot" :style="{ background: plan.color }"></div>
                    <span class="plan-name">{{ plan.name }}</span>
                  </div>
                  <span class="plan-count">{{ plan.value }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Secondary Bottom Grid -->
          <div class="dashboard-grid-secondary">
             <div class="orbit-card bottom-chart">
                <div class="card-header">
                  <h3>Spec Upload Activity</h3>
                  <div class="trend-summary positive">
                    <TrendingUp :size="14" class="mr-1" />
                    <span>Active uploads detected</span>
                  </div>
                </div>
                <div class="chart-box-sm">
                  <canvas id="specChart"></canvas>
                </div>
             </div>
             <div class="orbit-card bottom-chart">
                <div class="card-header">
                  <h3>Execution Performance</h3>
                  <div class="trend-summary" :class="stats.executions.success_rate >= 80 ? 'positive' : 'negative'">
                    <TrendingDown v-if="stats.executions.success_rate < 80" :size="14" class="mr-1" />
                    <TrendingUp v-else :size="14" class="mr-1" />
                    <span>Stability: {{ stats.executions.success_rate >= 80 ? 'High' : 'Moderate' }}</span>
                  </div>
                </div>
                <div class="chart-box-sm">
                  <canvas id="execChart"></canvas>
                </div>
             </div>
          </div>
        </template>

        <!-- Users Tab Content -->
        <template v-else-if="activeTab === 'users'">
          <div class="table-container">
            <div class="card-header user-table-header">
              <h3>Registered Users</h3>
              <div class="action-group">
                <div class="filter-pill-container">
                  <button v-for="p in ['all','free','starter','team','pro']" :key="p"
                    class="filter-pill" :class="{ active: userPlanFilter === p }"
                    @click="setUserFilter(p)">
                    {{ p }}
                  </button>
                </div>
                <!-- Role Filter -->
                <div class="filter-pill-container">
                  <button v-for="r in ['all', 'admin', 'normal']" :key="r"
                    class="filter-pill" :class="{ active: userRoleFilter === r }"
                    @click="setRoleFilter(r)">
                    {{ r }}
                  </button>
                </div>
                <button class="btn-primary-modern create-admin-btn" @click="showAdminModal = true">
                  <Plus :size="16" class="mr-1" />
                  Create Admin
                </button>
              </div>
            </div>
            
            <div class="orbit-card table-card p-0">
              <table class="modern-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Email Address</th>
                    <th>Sub Plan</th>
                    <th>Role</th>
                    <th>Date Joined</th>
                    <th class="text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="u in users" :key="u.id">
                    <td>
                      <div class="user-row">
                        <div class="user-avatar-modern">{{ u.name?.[0]?.toUpperCase() }}</div>
                        <span class="font-bold text-white">{{ u.name || 'Anonymous' }}</span>
                      </div>
                    </td>
                    <td class="text-gray-400">{{ u.email }}</td>
                    <td><span class="plan-pill" :class="u.plan">{{ u.plan }}</span></td>
                    <td>
                      <div class="role-badge" :class="{ admin: u.is_admin }">
                        <ShieldCheck v-if="u.is_admin" :size="12" class="mr-1" />
                        {{ u.is_admin ? 'Admin' : 'Normal User' }}
                      </div>
                    </td>
                    <td class="text-gray-500">{{ formatDate(u.created_at) }}</td>
                    <td class="text-right">
                      <div class="table-actions">
                        <button class="t-btn" title="Edit User" @click="startEditUser(u)">
                          <Pencil :size="16" class="text-gray-400 group-hover:text-primary" />
                        </button>
                        <button class="t-btn delete" title="Delete User" @click="confirmDeleteUser(u)">
                          <Trash2 :size="16" class="text-red-500/80" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="table-footer">
                <div class="pagination-modern">
                  <button :disabled="userPage <= 1" @click="userPage--;loadUsers()" class="p-btn">Prev</button>
                  <span class="p-info">Page {{ userPage }}</span>
                  <button :disabled="users.length < 20" @click="userPage++;loadUsers()" class="p-btn">Next</button>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- Activity Tab Content -->
        <template v-else-if="activeTab === 'activity'">
          <div class="table-container">
            <div class="card-header mb-6">
              <div class="title-group-sm">
                <h3>Recent System Activity</h3>
                <p class="text-xs text-gray-500 mt-1">Real-time execution logs and user interactions</p>
              </div>
              
              <!-- Activity Filters -->
              <div class="activity-filters-row">
                <div class="filter-group">
                  <label>Journey</label>
                  <input v-model="activitySearch" type="text" placeholder="Search journey..." class="f-input" />
                </div>
                <div class="filter-group">
                  <label>User</label>
                  <input v-model="activityUserSearch" type="text" placeholder="Search user..." class="f-input" />
                </div>
                <div class="filter-group">
                  <label>Status</label>
                  <select v-model="activityStatusFilter" class="f-select">
                    <option value="all">All Status</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                    <option value="running">Running</option>
                  </select>
                </div>
                <div class="filter-group duration-range">
                  <label>Duration (s)</label>
                  <div class="flex items-center gap-2">
                    <input v-model="activityDurationMin" type="number" placeholder="Min" class="f-input-sm" />
                    <span class="text-gray-600">-</span>
                    <input v-model="activityDurationMax" type="number" placeholder="Max" class="f-input-sm" />
                  </div>
                </div>
              </div>
            </div>
            
            <div class="orbit-card table-card p-0">
              <div v-if="filteredActivity.length === 0" class="no-results p-20 text-center">
                <div class="text-gray-500 font-bold mb-2">No activities found matching filters</div>
                <button class="btn-ghost text-primary text-xs" @click="activitySearch='';activityUserSearch='';activityStatusFilter='all';activityDurationMin='';activityDurationMax=''">Clear Filters</button>
              </div>
              <table v-else class="modern-table">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Journey Name</th>
                    <th>Executed By</th>
                    <th>Time Started</th>
                    <th>Duration</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in filteredActivity" :key="a.execution_id">
                    <td>
                      <div class="status-marker" :class="a.status">
                        <div class="status-dot-inner"></div>
                        {{ a.status }}
                      </div>
                    </td>
                    <td class="font-medium text-gray-300">{{ a.journey_name }}</td>
                    <td>
                      <div class="user-row">
                        <div class="user-avatar-modern sm">{{ a.user_name?.[0]?.toUpperCase() }}</div>
                        <div class="flex flex-col">
                          <span class="text-xs font-bold text-white">{{ a.user_name }}</span>
                          <span class="text-[10px] text-gray-500">{{ a.user_email }}</span>
                        </div>
                      </div>
                    </td>
                    <td class="text-gray-500">{{ formatDateTime(a.started_at) }}</td>
                    <td class="text-gray-500 font-mono text-xs">
                      {{ getActivityDuration(a) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>

        <!-- Settings Tab Content -->
        <template v-else-if="activeTab === 'settings'">
          <div class="settings-container">
            <div class="orbit-card settings-card">
              <div class="settings-section">
                <h3>Admin Profile</h3>
                <p class="section-desc">Manage your administrator account details</p>
                
                <div class="profile-form mt-8">
                  <div class="form-field">
                    <label>Display Name</label>
                    <input v-model="adminUpdateData.name" type="text" :placeholder="authStore.user?.name" />
                  </div>
                  <div class="form-field">
                    <label>Email Address</label>
                    <input v-model="adminUpdateData.email" type="email" :placeholder="authStore.user?.email" />
                  </div>
                  <div class="settings-actions">
                    <button class="btn-primary-modern" @click="updateSelf" :disabled="updatingProfile">
                      {{ updatingProfile ? 'Saving...' : 'Update Profile' }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="nav-divider"></div>

              <div class="settings-section">
                <h3>System Preferences</h3>
                <div class="preference-item mt-6">
                  <div class="pref-info">
                    <div class="pref-label">Display Theme</div>
                    <div class="pref-desc">Switch between light and dark dashboard modes</div>
                  </div>
                  <button class="theme-toggle-btn" @click="toggleTheme">
                    <Sun v-if="theme === 'dark'" :size="20" />
                    <Moon v-else :size="20" />
                    <span class="ml-2">{{ theme === 'dark' ? 'Light Mode' : 'Dark Mode' }}</span>
                  </button>
                </div>
              </div>

              <div class="nav-divider"></div>

              <div class="settings-section danger">
                <h3>Danger Zone</h3>
                <div class="preference-item mt-6">
                  <div class="pref-info">
                    <div class="pref-label">Disable Admin Access</div>
                    <div class="pref-desc">Remove your administrative privileges (cannot be undone)</div>
                  </div>
                  <button class="btn-ghost text-red-500 hover:bg-red-500/10" @click="confirmSelfDemote">
                    Revoke Access
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Loading State Cover -->
      <div v-if="loading && !stats" class="global-loader">
        <div class="loader-ripple">
          <div></div><div></div>
        </div>
        <p class="mt-4 font-black tracking-widest text-primary text-xs uppercase">Syncing Platform Data...</p>
      </div>
    </main>

    <!-- Modal for Admin Creation -->
    <Transition name="fade-scale">
      <div v-if="showAdminModal" class="orbit-modal-overlay" @click.self="showAdminModal = false">
        <div class="orbit-modal-box">
          <div class="modal-glow"></div>
          <h2 class="text-2xl font-black mb-2">Create Admin Access</h2>
          <p class="text-sm text-gray-500 mb-8">Grant privileged access to the platform analytics and user management.</p>
          
          <form @submit.prevent="createAdmin" class="space-y-6">
            <div class="form-field">
              <label>Full Name</label>
              <input v-model="newAdmin.name" type="text" placeholder="Alex Rivera" required />
            </div>
            <div class="form-field">
              <label>Email ID</label>
              <input v-model="newAdmin.email" type="email" placeholder="alex@specflow.com" required />
            </div>
            <div class="form-field">
              <label>Secure Password</label>
              <div class="relative">
                <input v-model="newAdmin.password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" required minlength="8" />
                <button type="button" @click="showPassword = !showPassword" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500">
                  <Eye v-if="!showPassword" :size="18" />
                  <EyeOff v-else :size="18" />
                </button>
              </div>
            </div>
            
            <div v-if="adminFormError" class="error-msg">{{ adminFormError }}</div>
            <div v-if="adminFormSuccess" class="success-msg">{{ adminFormSuccess }}</div>
            
            <div class="modal-footer flex justify-between items-center pt-6">
              <button type="button" class="btn-ghost" @click="showAdminModal = false">Cancel</button>
              <button type="submit" class="btn-primary-modern px-8" :disabled="creatingAdmin">
                {{ creatingAdmin ? 'Provisioning...' : 'Provision Admin' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- Modal for User Editing -->
    <Transition name="fade-scale">
      <div v-if="showEditModal" class="orbit-modal-overlay" @click.self="showEditModal = false">
        <div class="orbit-modal-box">
          <div class="modal-glow"></div>
          <h2 class="text-2xl font-black mb-2">Edit User Profile</h2>
          <p class="text-sm text-gray-500 mb-8">Modify account details and platform privileges.</p>
          
          <form @submit.prevent="updateUserDetails" class="space-y-6">
            <div class="form-field">
              <label>Full Name</label>
              <input v-model="editUserData.name" type="text" placeholder="Alex Rivera" required />
            </div>
            <div class="form-field">
              <label>Email ID</label>
              <input v-model="editUserData.email" type="email" placeholder="alex@specflow.com" required />
            </div>
            
            <div class="flex items-center gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
              <input type="checkbox" v-model="editUserData.is_admin" id="isAdminCheck" class="w-5 h-5 accent-primary" />
              <label for="isAdminCheck" class="mb-0 cursor-pointer text-sm font-bold text-white">Administrator Access</label>
            </div>
            
            <div v-if="editFormError" class="error-msg text-red-500 text-sm font-bold">{{ editFormError }}</div>
            
            <div class="modal-footer flex justify-between items-center pt-6">
              <button type="button" class="btn-ghost" @click="showEditModal = false">Cancel</button>
              <button type="submit" class="btn-primary-modern px-8" :disabled="updatingUser">
                {{ updatingUser ? 'Saving...' : 'Save Changes' }}
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
import { useToast } from 'vue-toastification'
import apiClient from '@/api/client'
import { 
  Users, 
  FileCode2, 
  Map, 
  Zap, 
  Activity, 
  LayoutDashboard, 
  Settings, 
  Bell, 
  Search, 
  RefreshCw,
  MoreVertical,
  TrendingUp,
  TrendingDown,
  ChevronLeft,
  Eye,
  EyeOff,
  Sun,
  Moon,
  Plus,
  ShieldCheck,
  Trash2,
  Pencil
} from 'lucide-vue-next'

const authStore = useAuthStore()
const toast = useToast()

// ── Tabs ──────────────────────────────────────────────────────────
const tabs = [
  { id: 'overview', label: 'Overview', description: 'Platform-wide analytics', icon: LayoutDashboard },
  { id: 'users',    label: 'Users',    description: 'Registered accounts',   icon: Users },
  { id: 'activity', label: 'Activity', description: 'Execution logs',        icon: Activity },
  { id: 'settings', label: 'Settings', description: 'Platform config',       icon: Settings },
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
const userRoleFilter = ref('all')
const lastUpdated = ref('—')
const searchQuery = ref('')
const sidebarCollapsed = ref(false)
const showPassword = ref(false)
const theme = ref('dark')

// Activity Filtering State
const activitySearch = ref('')
const activityUserSearch = ref('')
const activityStatusFilter = ref('all')
const activityDurationMin = ref('')
const activityDurationMax = ref('')

const adminUpdateData = ref({ 
  name: authStore.user?.name || '', 
  email: authStore.user?.email || '' 
})
const updatingProfile = ref(false)

// Mini Chart (Sparkline) logic
const sparklineData = ref({
  users: [30, 45, 32, 60, 55, 70, 65],
  specs: [10, 20, 15, 25, 30, 28, 35],
  journeys: [5, 12, 8, 15, 20, 18, 25],
  success: [80, 85, 82, 88, 90, 89, 92]
})

// Chart instances
let planChart = null
let userGrowthChartInst = null
let specChartInst = null
let execChartInst = null
let sparkCharts = {}

// Modal
const showAdminModal  = ref(false)
const creatingAdmin   = ref(false)
const adminFormError  = ref('')
const adminFormSuccess = ref('')
const newAdmin = ref({ name: '', email: '', password: '' })

// Edit User State
const showEditModal = ref(false)
const editingUser = ref(null)
const editUserData = ref({ name: '', email: '', is_admin: false })
const updatingUser = ref(false)
const editFormError = ref('')

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
  let roleParam = ''
  if (userRoleFilter.value === 'admin') roleParam = '&is_admin=true'
  else if (userRoleFilter.value === 'normal') roleParam = '&is_admin=false'
  
  const { data } = await apiClient.get(`/api/admin/users?page=${userPage.value}&limit=20${plan}${roleParam}`)
  users.value = data
}

async function loadActivity() {
  const { data } = await apiClient.get('/api/admin/recent-activity?limit=100')
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

async function setRoleFilter(r) {
  userRoleFilter.value = r
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
    toast.success(adminFormSuccess.value)
    newAdmin.value = { name: '', email: '', password: '' }
    await loadUsers()
  } catch (e) {
    adminFormError.value = e.response?.data?.detail || 'Failed to create admin'
    toast.error(adminFormError.value)
  } finally {
    creatingAdmin.value = false
  }
}

// ── User Management ────────────────────────────────────────────────
function startEditUser(user) {
  editingUser.value = user
  editUserData.value = { 
    name: user.name || '', 
    email: user.email || '', 
    is_admin: user.is_admin || false 
  }
  showEditModal.value = true
}

async function updateUserDetails() {
  updatingUser.value = true
  editFormError.value = ''
  try {
    await apiClient.patch(`/api/admin/users/${editingUser.value.id}`, editUserData.value)
    showEditModal.value = false
    toast.success(`User ${editUserData.value.email} updated successfully!`)
    await loadUsers()
  } catch (e) {
    editFormError.value = e.response?.data?.detail || 'Failed to update user'
    toast.error(editFormError.value)
  } finally {
    updatingUser.value = false
  }
}

async function confirmDeleteUser(user) {
  if (confirm(`Are you sure you want to delete user ${user.email}? This action cannot be undone.`)) {
    try {
      await apiClient.delete(`/api/admin/users/${user.id}`)
      toast.success(`User ${user.email} deleted successfully!`)
      await loadUsers()
    } catch (e) {
      const error = e.response?.data?.detail || 'Failed to delete user'
      toast.error(error)
    }
  }
}

async function toggleAdmin(user) {
  try {
    await apiClient.patch(`/api/admin/users/${user.id}`, { is_admin: !user.is_admin })
    await loadUsers()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to toggle admin status')
  }
}

async function changePlan(user, plan) {
  try {
    await apiClient.patch(`/api/admin/users/${user.id}`, { plan })
    await loadUsers()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to change plan')
  }
}

// ── Activity Filtering Logic ──────────────────────────────────────
const filteredActivity = computed(() => {
  if (!activity.value) return []
  
  return activity.value.filter(a => {
    // Journey Filter
    if (activitySearch.value && !a.journey_name.toLowerCase().includes(activitySearch.value.toLowerCase())) {
      return false
    }
    
    // User Filter
    if (activityUserSearch.value) {
      const search = activityUserSearch.value.toLowerCase()
      const matchesName = a.user_name?.toLowerCase().includes(search)
      const matchesEmail = a.user_email?.toLowerCase().includes(search)
      if (!matchesName && !matchesEmail) return false
    }
    
    // Status Filter
    if (activityStatusFilter.value !== 'all' && a.status !== activityStatusFilter.value) {
      return false
    }
    
    // Duration Filter
    if (a.completed_at && a.started_at) {
      const start = new Date(a.started_at)
      const end = new Date(a.completed_at)
      const durationSec = (end - start) / 1000
      
      const min = parseFloat(activityDurationMin.value)
      const max = parseFloat(activityDurationMax.value)
      
      if (!isNaN(min) && durationSec < min) return false
      if (!isNaN(max) && durationSec > max) return false
    } else if (activityDurationMin.value || activityDurationMax.value) {
      // If filtering by duration but it's still running, it doesn't have a final duration
      if (a.status === 'running') return false
    }
    
    return true
  })
})

function getActivityDuration(a) {
  if (!a.completed_at || !a.started_at) return 'Running...'
  const start = new Date(a.started_at)
  const end = new Date(a.completed_at)
  const diffSec = (end - start) / 1000
  return diffSec.toFixed(1) + 's'
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
    color: planColors[name] || '#888'
  }))
})

// ── Admin Profile Actions ──────────────────────────────────────────
async function updateSelf() {
  updatingProfile.value = true
  try {
    const { data } = await apiClient.patch(`/api/admin/users/${authStore.user.id}`, adminUpdateData.value)
    authStore.user = data
    alert('Profile updated successfully!')
  } catch (e) {
    alert(e.response?.data?.detail || 'Update failed')
  } finally {
    updatingProfile.value = false
  }
}

function confirmSelfDemote() {
  if (confirm('Are you sure you want to revoke your admin status? You will lose access to this dashboard immediately.')) {
    apiClient.patch(`/api/admin/users/${authStore.user.id}`, { is_admin: false }).then(() => {
      window.location.href = '/dashboard'
    })
  }
}

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  document.documentElement.classList.toggle('light-theme')
}

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
  renderSparklines()
}

function renderSparklines() {
  const configs = [
    { id: 'sparkUsers', color: '#A78BFA', data: sparklineData.value.users },
    { id: 'sparkSpecs', color: '#22D3EE', data: sparklineData.value.specs },
    { id: 'sparkJourneys', color: '#BFF549', data: sparklineData.value.journeys },
    { id: 'sparkManual', color: '#60A5FA', data: [12, 18, 15, 22, 19, 25, 21] },
    { id: 'sparkSuccess', color: '#F43F5E', data: sparklineData.value.success }
  ]

  configs.forEach(conf => {
    const ctx = document.getElementById(conf.id)
    if (!ctx) return
    
    if (sparkCharts[conf.id]) sparkCharts[conf.id].destroy()

    sparkCharts[conf.id] = new window.Chart(ctx, {
      type: 'line',
      data: {
        labels: conf.data.map((_, i) => i),
        datasets: [{
          data: conf.data,
          borderColor: conf.color,
          borderWidth: 2,
          pointRadius: 0,
          fill: true,
          backgroundColor: conf.color + '10',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: { 
          x: { display: false }, 
          y: { display: false, beginAtZero: true } 
        },
        animation: { duration: 800 },
        events: []
      }
    })
  })
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
      cutout: '72%',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { 
        legend: { display: false },
        tooltip: {
          backgroundColor: '#111',
          titleFont: { family: 'Outfit', size: 14, weight: 'bold' },
          bodyFont: { family: 'Outfit', size: 13 },
          padding: 12,
          cornerRadius: 10,
          displayColors: true
        }
      },
      animation: { animateScale: true, duration: 800 }
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
    maintainAspectRatio: false,
    plugins: { 
      legend: { 
        position: 'top',
        align: 'start',
        labels: { 
          color: textColor, 
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 20,
          font: { family: 'Outfit', size: 12, weight: '600' } 
        } 
      } 
    },
    scales: {
      x: { 
        ticks: { color: textColor, maxTicksLimit: 8, font: { family: 'Outfit', size: 11 } }, 
        grid: { color: gridColor, drawTicks: false } 
      },
      y: { 
        ticks: { color: textColor, font: { family: 'Outfit', size: 11 }, padding: 10 }, 
        grid: { color: gridColor, drawTicks: false }, 
        beginAtZero: true 
      }
    },
    layout: {
      padding: { top: 10, right: 10, bottom: 0, left: 0 }
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
            borderColor: '#ff4d4d',
            backgroundColor: 'rgba(255, 77, 77, 0.15)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#ff4d4d',
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 3,
            borderDash: [5, 5] // Differentiate failed with dashed line
          }
        ]
      },
      options: {
        ...baseOpts,
        scales: {
          ...baseOpts.scales,
          y: {
            ...baseOpts.scales.y,
            suggestedMax: 5 // Ensure some headroom even if values are low
          }
        }
      }
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

// Resize charts when sidebar state changes
watch(sidebarCollapsed, () => {
  setTimeout(() => {
    if (planChart) planChart.resize()
    if (userGrowthChartInst) userGrowthChartInst.resize()
    if (specChartInst) specChartInst.resize()
    if (execChartInst) execChartInst.resize()
    // Small delay to allow CSS transitions to finish
  }, 310)
})

onMounted(loadAll)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

/* ── Root Layout ── */
.admin-wrapper {
  display: flex;
  height: 100vh;
  background: #000000;
  color: #ffffff;
  font-family: 'Outfit', sans-serif;
  overflow: hidden;
}

/* ── Sidebar ── */
.admin-sidebar {
  width: 280px;
  background: #000000;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  z-index: 50;
}
.sidebar-collapsed .admin-sidebar { width: 80px; }

.sidebar-header {
  padding: 32px 24px;
  height: 100px;
  display: flex;
  align-items: center;
}
.admin-label {
  font-size: 10px;
  background: #BFF549;
  color: #000;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 8px;
  font-weight: 900;
  letter-spacing: 0.05em;
}

.sidebar-content {
  flex: 1;
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.nav-section {
  color: #444;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 24px 12px 8px;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  color: #888;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s;
  background: transparent;
  border: none;
  width: 100%;
  cursor: pointer;
  position: relative;
}
.nav-icon {
  flex-shrink: 0;
  transition: transform 0.2s;
}
.sidebar-collapsed .nav-link:hover .nav-icon {
  transform: scale(1.2);
  color: #BFF549;
}
.nav-link:hover { color: #fff; background: rgba(255,255,255,0.05); }
.sidebar-collapsed .nav-link {
  justify-content: center;
  padding: 12px 0;
  width: 48px;
  margin: 0 auto;
}
.sidebar-collapsed .nav-icon {
  margin: 0;
}
.nav-link.active { color: #BFF549; background: rgba(191,245,73,0.08); font-weight: 600; }
.active-indicator {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: #BFF549;
  border-radius: 3px 0 0 3px;
  box-shadow: 0 0 10px #BFF549;
}
.nav-divider { height: 1px; background: rgba(255,255,255,0.05); margin: 16px 12px; }

.sidebar-footer { padding: 24px; border-top: 1px solid rgba(255,255,255,0.05); }
.user-profile-summary { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.avatar-ring { position: relative; width: 42px; height: 42px; }
.avatar-inner {
  width: 100%; height: 100%; border-radius: 14px;
  background: linear-gradient(135deg, #222, #111);
  border: 1px solid rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #BFF549;
}
.status-dot {
  position: absolute; bottom: -2px; right: -2px;
  width: 12px; height: 12px; border-radius: 50%;
  background: #BFF549; border: 3px solid #000;
}
.user-name { font-size: 14px; font-weight: 700; color: #fff; }
.user-role { font-size: 11px; color: #555; }
.collapse-toggle {
  width: 100%; padding: 10px; border-radius: 12px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  color: #BFF549; font-size: 13px; font-weight: 700; cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex; align-items: center; justify-content: center;
}
.sidebar-collapsed .collapse-toggle {
  width: 44px;
  padding: 10px 0;
  margin: 0 auto;
}
.collapse-toggle:hover { 
  color: #000; background: #BFF549; 
  border-color: #BFF549;
  box-shadow: 0 4px 15px rgba(191,245,73,0.5);
  transform: scale(1.05);
}

/* ── Main Content Area ── */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #000;
  position: relative;
  overflow: hidden;
}

/* ── Top Header ── */
.admin-header {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(10px);
  z-index: 40;
}
.header-search {
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.04);
  padding: 0 20px;
  border-radius: 14px;
  width: 320px;
  border: 1px solid rgba(255,255,255,0.05);
  transition: all 0.2s;
}
.header-search:focus-within { border-color: #BFF549; background: rgba(255,255,255,0.07); width: 400px; }
.search-icon { color: #555; margin-right: 12px; }
.header-search input {
  background: transparent; border: none; color: #fff;
  padding: 12px 0; font-size: 14px; width: 100%; outline: none;
}
.header-actions { display: flex; align-items: center; gap: 32px; }
.action-icons { display: flex; align-items: center; gap: 12px; }
.icon-btn {
  width: 42px; height: 42px; border-radius: 12px;
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
  color: #888; cursor: pointer; display: flex; align-items: center; justify-content: center;
  position: relative; transition: all 0.2s;
}
.icon-btn:hover { background: rgba(255,255,255,0.08); color: #fff; transform: translateY(-2px); }
.notification-badge {
  position: absolute; top: 10px; right: 10px;
  width: 8px; height: 8px; background: #BFF549;
  border-radius: 50%; border: 2px solid #000;
}
.user-dropdown { padding-left: 20px; border-left: 1px solid rgba(255,255,255,0.05); }
.dropdown-trigger { display: flex; align-items: center; cursor: pointer; }
.mini-avatar {
  width: 36px; height: 36px; border-radius: 10px;
  background: #BFF549; color: #000; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
}

/* ── Container ── */
.admin-container {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}
.container-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 40px;
}
.title-group h2 { font-size: 32px; font-weight: 900; margin: 0; }
.title-group p { color: #666; font-size: 15px; margin-top: 4px; }
.last-sync { color: #444; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; }

/* ── Cards & Widgets ── */
.orbit-card {
  background: #0A0A0A;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 24px;
  padding: 24px;
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}
.kpi-widget {
  position: relative;
  overflow: hidden;
  height: 180px;
  display: flex;
  flex-direction: column;
}
.widget-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.widget-title { display: flex; align-items: center; gap: 12px; font-size: 13px; font-weight: 700; color: #888; }
.icon-box {
  width: 34px; height: 34px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.03);
}
.widget-value-group { display: flex; align-items: baseline; gap: 8px; margin-bottom: 2px; }
.widget-sub-label { font-size: 10px; color: #555; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; }
.widget-value { font-size: 32px; font-weight: 900; color: #fff; line-height: 1; }
.widget-footer { font-size: 11px; color: #444; font-weight: 700; text-transform: uppercase; margin-top: auto; }
.trend { font-size: 12px; font-weight: 800; padding: 4px 8px; border-radius: 8px; }
.trend.positive { background: rgba(191,245,73,0.1); color: #BFF549; }
.trend.negative { background: rgba(248,113,113,0.1); color: #F87171; }

.widget-spark {
  position: absolute; bottom: 0; left: 0; right: 0; height: 60px;
  opacity: 0.4; pointer-events: none;
}

/* Colored Accents */
.kpi-widget.purple .icon-box { color: #A78BFA; }
.kpi-widget.cyan .icon-box { color: #22D3EE; }
.kpi-widget.lime .icon-box { color: #BFF549; }
.kpi-widget.rose .icon-box { color: #F43F5E; }
.kpi-widget.indigo .icon-box { color: #6366F1; }

/* ── Charts Grid ── */
.dashboard-grid {
  display: grid;
  grid-template-columns: 2.5fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.card-header h3 { font-size: 18px; font-weight: 800; }

.chart-labels { display: flex; gap: 16px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #555; font-weight: 700; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.lime { background: #BFF549; box-shadow: 0 0 10px #BFF549; }
.dot.gray { background: #333; }

.period-select {
  background: #111; border: 1px solid #222; color: #888;
  padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 700; outline: none;
}

.chart-content { height: 350px; }

/* Side Chart (Donut) */
.donut-content { position: relative; height: 260px; margin-bottom: 24px; display: flex; align-items: center; justify-content: center; }
.donut-center {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.total-val { font-size: 42px; font-weight: 900; line-height: 1; margin-bottom: 2px; color: #fff; }
.total-label { font-size: 12px; color: #888; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; }

.plan-list { display: flex; flex-direction: column; gap: 12px; }
.plan-item { display: flex; justify-content: space-between; align-items: center; }
.plan-info { display: flex; align-items: center; gap: 10px; }
.plan-dot { width: 10px; height: 10px; border-radius: 3px; }
.plan-name { font-size: 13px; font-weight: 600; color: #888; }
.plan-count { font-size: 13px; font-weight: 800; color: #fff; }

/* Bottom Charts */
.dashboard-grid-secondary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.trend-summary { display: flex; align-items: center; font-size: 11px; font-weight: 800; text-transform: uppercase; }
.trend-summary.positive { color: #BFF549; }
.trend-summary.negative { color: #F87171; }
.chart-box-sm { height: 180px; }

/* ── Tables ── */
.table-container { margin-top: 20px; }
.filter-pill-container {
  display: flex; background: #0A0A0A; padding: 4px;
  border-radius: 12px; border: 1px solid #222;
}
.filter-pill {
  padding: 6px 16px; border-radius: 8px; font-size: 12px; font-weight: 700;
  color: #555; border: none; background: transparent; cursor: pointer; transition: all 0.2s;
}
.filter-pill.active { background: #BFF549; color: #000; box-shadow: 0 4px 12px rgba(191,245,73,0.3); }

.modern-table { width: 100%; border-collapse: collapse; }
.modern-table th {
  text-align: left; padding: 20px 24px; font-size: 12px; color: #444;
  font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em;
  border-bottom: 1px solid #111;
}
.modern-table td { padding: 18px 24px; vertical-align: middle; border-bottom: 1px solid #0D0D0D; }
.modern-table tr:hover { background: rgba(255,255,255,0.01); }

.user-row { display: flex; align-items: center; gap: 12px; }
.user-avatar-modern {
  width: 36px; height: 36px; border-radius: 10px;
  background: #111; color: #fff; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid #222;
}
.user-avatar-modern.sm { width: 30px; height: 30px; font-size: 10px; }

.plan-pill {
  padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.05em;
}
.plan-pill.free { background: #222; color: #888; }
.plan-pill.pro { background: rgba(167,139,250,0.1); color: #A78BFA; }
.plan-pill.team { background: rgba(191,245,73,0.1); color: #BFF549; }

.role-badge {
  display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 20px;
  font-size: 10px; font-weight: 800; color: #444; background: #111;
}
.role-badge.admin { color: #BFF549; background: rgba(191,245,73,0.1); }

.table-actions { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }
.t-btn {
  width: 32px; height: 32px; border-radius: 8px; background: #111; border: 1px solid #222;
  color: #666; cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.t-btn:hover { border-color: #BFF549; color: #BFF549; }
.t-btn.delete:hover { border-color: #F87171; }
.t-select {
  background: #111; border: 1px solid #222; color: #888;
  padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;
}

.table-footer { padding: 24px; border-top: 1px solid #111; }
.pagination-modern { display: flex; justify-content: flex-end; align-items: center; gap: 16px; }
.p-btn {
  padding: 8px 16px; border-radius: 8px; background: #111; border: 1px solid #222;
  color: #888; font-weight: 700; cursor: pointer;
}
.p-btn:hover:not(:disabled) { border-color: #BFF549; color: #fff; }
.p-info { font-size: 12px; color: #444; font-weight: 700; }

/* Status Marker */
.status-marker {
  display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px;
  border-radius: 20px; font-size: 11px; font-weight: 800; text-transform: capitalize;
}
.status-marker.completed { background: rgba(191,245,73,0.1); color: #BFF549; }
.status-marker.failed { background: rgba(248,113,113,0.1); color: #F87171; }
.status-marker.running { background: rgba(251,191,36,0.1); color: #FBBF24; }
.status-dot-inner { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

/* ── Global Loader ── */
.global-loader {
  position: absolute; inset: 0; background: #000; z-index: 100;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.loader-ripple {
  position: relative; width: 80px; height: 80px;
}
.loader-ripple div {
  position: absolute; border: 4px solid #BFF549; opacity: 1; border-radius: 50%;
  animation: loader-ripple 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
}
.loader-ripple div:nth-child(2) { animation-delay: -0.5s; }
@keyframes loader-ripple {
  0% { top: 36px; left: 36px; width: 0; height: 0; opacity: 1; }
  100% { top: 0px; left: 0px; width: 72px; height: 72px; opacity: 0; }
}

/* ── Modals ── */
.orbit-modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(10px);
  z-index: 200; display: flex; align-items: center; justify-content: center;
}
.orbit-modal-box {
  width: 440px; background: #0A0A0A; border-radius: 32px; padding: 40px;
  border: 1px solid rgba(255,255,255,0.08); position: relative; overflow: hidden;
}
.modal-glow {
  position: absolute; top: -50%; right: -50%; width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(191,245,73,0.15) 0%, transparent 70%);
}

.form-field { margin-bottom: 20px; }
.form-field label { display: block; font-size: 11px; font-weight: 800; color: #444; text-transform: uppercase; margin-bottom: 8px; }
.form-field input {
  width: 100%; background: #111; border: 1px solid #222; border-radius: 14px;
  padding: 14px 20px; color: #fff; font-size: 14px; transition: all 0.2s;
}
.form-field input:focus { border-color: #BFF549; outline: none; background: #151515; }

.btn-primary-modern {
  background: #BFF549; color: #000; border: none; padding: 14px 28px;
  border-radius: 14px; font-weight: 800; font-size: 14px; cursor: pointer;
  box-shadow: 0 8px 24px rgba(191,245,73,0.3); transition: all 0.2s;
}
.btn-primary-modern:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(191,245,73,0.4); }

.btn-ghost { background: transparent; border: none; color: #555; font-weight: 700; cursor: pointer; }
.btn-ghost:hover { color: #fff; }

.btn-primary-sm {
  background: #BFF549; color: #000; border: none; padding: 8px 16px;
  border-radius: 10px; font-weight: 800; font-size: 12px; cursor: pointer;
}

/* Animations */
.spinning { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.fade-scale-enter-active, .fade-scale-leave-active { transition: all 0.3s ease; }
.fade-scale-enter-from, .fade-scale-leave-to { opacity: 0; transform: scale(0.95); }

/* Scrollbar Hide */
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }

/* ── Tab Layout Fixes ── */
.user-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.user-table-header h3 { font-size: 20px; font-weight: 900; }

/* ── Activity Filters ── */
.activity-filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: flex-end;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-group label {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  color: #444;
  letter-spacing: 0.1em;
}
.f-input, .f-select {
  background: #111;
  border: 1px solid #222;
  border-radius: 8px;
  padding: 8px 12px;
  color: #fff;
  font-size: 13px;
  outline: none;
  transition: all 0.2s;
}
.f-input:focus, .f-select:focus {
  border-color: #BFF549;
  background: #151515;
}
.f-input-sm {
  width: 70px;
  background: #111;
  border: 1px solid #222;
  border-radius: 8px;
  padding: 8px;
  color: #fff;
  font-size: 12px;
  outline: none;
}
.f-input-sm:focus { border-color: #BFF549; }
.duration-range { min-width: 160px; }

.action-group {
  display: flex;
  align-items: center;
  gap: 16px;
}
.create-admin-btn {
  padding: 10px 18px;
  font-size: 13px;
  box-shadow: 0 4px 12px rgba(191,245,73,0.2);
}

/* ── Settings View ── */
.settings-container { max-width: 800px; margin: 0 auto; }
.settings-card { padding: 40px; }
.settings-section h3 { font-size: 20px; font-weight: 900; margin-bottom: 8px; }
.section-desc { font-size: 14px; color: #666; margin-bottom: 24px; }
.preference-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}
.pref-label { font-size: 15px; font-weight: 700; color: #fff; }
.pref-desc { font-size: 13px; color: #555; }
.theme-toggle-btn {
  display: flex;
  align-items: center;
  background: #111;
  border: 1px solid #222;
  color: #fff;
  padding: 10px 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.theme-toggle-btn:hover { border-color: #BFF549; color: #BFF549; }
.settings-actions { margin-top: 24px; }

/* ── Light Mode Support ── */
:root.light-theme {
  --bg: #f8f9fa;
  --card: #ffffff;
  --border: rgba(0,0,0,0.05);
  --text: #1a1a1a;
  --muted: #666;
}
.light-theme .admin-wrapper { background: #f0f2f5; color: #1a1a1a; }
.light-theme .admin-sidebar, 
.light-theme .admin-main,
.light-theme .admin-header { background: #fff; color: #1a1a1a; border-color: rgba(0,0,0,0.08); }
.light-theme .orbit-card { background: #fff; border-color: rgba(0,0,0,0.1); box-shadow: 0 4px 20px rgba(0,0,0,0.03); }
.light-theme .text-white,
.light-theme h2,
.light-theme h3,
.light-theme .widget-value,
.light-theme .total-val,
.light-theme .user-name,
.light-theme .plan-count,
.light-theme .pref-label { color: #1a1a1a !important; }
.light-theme .text-gray-400,
.light-theme .section-desc,
.light-theme .total-label,
.light-theme .pref-desc { color: #555 !important; }
.light-theme .text-gray-500 { color: #888 !important; }
.light-theme .nav-link:not(.active) { color: #555; }
.light-theme .nav-link:hover { background: rgba(0,0,0,0.03); }
.light-theme .form-field input,
.light-theme .t-select,
.light-theme .period-select { background: #f8f9fa; border-color: rgba(0,0,0,0.1); color: #1a1a1a; }
.light-theme .icon-btn { background: #f8f9fa; border-color: rgba(0,0,0,0.08); }
.light-theme .collapse-toggle { 
  background: #f8f9fa; 
  border-color: rgba(0,0,0,0.1); 
  color: #555; 
}
.light-theme .collapse-toggle:hover {
  background: #BFF549;
  color: #000;
  border-color: #BFF549;
}
.light-theme .mini-avatar { box-shadow: 0 4px 10px rgba(191,245,73,0.3); }

/* ── Mobile Responsiveness ── */
@media (max-width: 1024px) {
  .admin-sidebar { width: 80px; }
  .sidebar-header { padding: 24px 16px; justify-content: center; }
  .sidebar-content { padding: 0 10px; }
  .user-profile-summary { display: none; }
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
  .dashboard-grid { grid-template-columns: 1fr; }
  .dashboard-grid-secondary { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .admin-header { padding: 0 20px; height: 80px; }
  .header-search { display: none; }
  .admin-container { padding: 20px; }
  .container-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .title-group h2 { font-size: 24px; }
  .kpi-row { grid-template-columns: 1fr; }
  .admin-wrapper { flex-direction: column; }
  .admin-sidebar { 
    width: 100%; 
    height: auto; 
    flex-direction: row; 
    border-right: none; 
    border-bottom: 1px solid rgba(255,255,255,0.05); 
  }
  .sidebar-header { height: 60px; padding: 0 15px; border-bottom: none; }
  .sidebar-content { flex-direction: row; padding: 0 15px; overflow-x: auto; height: 60px; align-items: center; }
  .nav-link { width: auto; padding: 8px 12px; font-size: 13px; }
  .nav-section, .nav-divider, .sidebar-footer { display: none; }
  .admin-main { height: calc(100vh - 120px); }
  .table-card { overflow-x: auto; }
  .modern-table { min-width: 600px; }
  .settings-card { padding: 20px; }
}

@media (max-width: 480px) {
  .action-group { flex-direction: column; align-items: stretch; }
  .filter-pill-container { overflow-x: auto; white-space: nowrap; padding-bottom: 8px; }
  .icon-btn { width: 36px; height: 36px; }
  .header-actions { gap: 15px; }
}

</style>
