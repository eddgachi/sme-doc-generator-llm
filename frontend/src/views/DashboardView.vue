<template>
  <main class="container-fluid p-0">
    <!-- Header Action Bar -->
    <section class="d-flex flex-wrap align-items-center gap-3 mb-4 px-4 pb-3 border-bottom border-light-subtle">
      <!-- Action Buttons -->
      <div class="d-flex gap-2 flex-wrap">
        <button
          @click="triggerBulkUpload"
          class="btn btn-outline-success btn-sm"
          :disabled="isSyncing"
          v-tooltip="'Upload data from MySQL to Freshworks'"
        >
          <i class="fas fa-upload fa-fw me-1"></i> Bulk Upload
        </button>
        <button
          @click="triggerTwoWaySync"
          class="btn btn-primary btn-sm"
          :disabled="isSyncing"
          v-tooltip="'Run bidirectional data synchronization'"
        >
          <i class="fas fa-sync-alt fa-fw me-1"></i> Two-Way Sync
        </button>
        <button
          @click="refreshData"
          class="btn btn-outline-secondary btn-sm"
          :disabled="isSyncing"
          v-tooltip="'Fetch latest data'"
        >
          <i class="fas fa-redo fa-fw me-1"></i> Refresh
        </button>
      </div>

      <!-- Status Display -->
      <div class="ms-auto d-flex align-items-center gap-3 text-muted small">
        <div v-if="isSyncing" class="d-flex align-items-center text-primary">
          <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          <div class="d-flex flex-column">
            <span>{{ message }}</span>
            <span v-if="syncProgress.step" class="text-muted x-small">
              Step {{ syncProgress.step }}/{{ syncProgress.totalSteps }}: {{ syncProgress.message }}
              <span v-if="syncProgress.etr"> (Est. {{ syncProgress.etr }} remaining)</span>
            </span>
          </div>
        </div>
        <div v-else class="text-muted">{{ message }}</div>
        <span class="d-none d-md-inline vr"></span>
        <div class="d-none d-md-flex align-items-center" v-tooltip="'Status of the last completed sync'">
          <i
            :class="['fa-fw me-2', statusIcon(syncStatus.status), statusClass(syncStatus.status)]"
            :title="'Last Sync Status: ' + syncStatus.status"
          ></i>
          <span>Last: {{ syncStatus.lastSyncTime }}</span>
        </div>
      </div>
    </section>

    <!-- Loading State -->
    <div v-if="isLoading" class="px-4 mb-4">
      <div class="row g-4">
        <div v-for="n in 4" :key="'skel-metric-' + n" class="col-lg-3 col-md-6 col-6">
          <div class="skeleton-box" style="height: 100px"></div>
        </div>
        <div class="col-lg-8"><div class="skeleton-box" style="height: 300px"></div></div>
        <div class="col-lg-4"><div class="skeleton-box" style="height: 300px"></div></div>
        <div class="col-12"><div class="skeleton-box" style="height: 350px"></div></div>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="px-4">
      <!-- Metrics Cards -->
      <section class="mb-4">
        <div class="row g-3">
          <!-- Total Syncs Today -->
          <div class="col-lg-3 col-md-6 col-6">
            <div class="p-3 h-100 rounded border border-light-subtle dashboard-card">
              <div class="d-flex justify-content-between mb-1">
                <h3 class="text-muted small fw-normal mb-0">Total Syncs Today</h3>
                <i class="fas fa-hashtag text-primary opacity-50"></i>
              </div>
              <div class="d-flex align-items-baseline">
                <p class="fs-2 fw-bold mb-0 me-2">{{ metrics.totalSyncsToday }}</p>
                <span :class="['badge fw-medium small', syncTrendClass]" v-tooltip="'Compared to yesterday'">
                  <i :class="['fas me-1', syncTrendIcon]"></i>{{ syncTrendValue }}
                </span>
              </div>
            </div>
          </div>

          <!-- Success Rate -->
          <div class="col-lg-3 col-md-6 col-6">
            <div class="p-3 h-100 rounded border border-light-subtle dashboard-card">
              <div class="d-flex justify-content-between mb-1">
                <h3 class="text-muted small fw-normal mb-0">Success Rate</h3>
                <i class="fas fa-check-circle text-success opacity-50"></i>
              </div>
              <div class="d-flex align-items-baseline">
                <p class="fs-2 fw-bold mb-0 me-2">{{ metrics.successRate }}<small>%</small></p>
              </div>
            </div>
          </div>

          <!-- Avg Sync Time -->
          <div class="col-lg-3 col-md-6 col-6">
            <div class="p-3 h-100 rounded border border-light-subtle dashboard-card">
              <div class="d-flex justify-content-between mb-1">
                <h3 class="text-muted small fw-normal mb-0">Avg Sync Time</h3>
                <i class="fas fa-hourglass-half text-info opacity-50"></i>
              </div>
              <div class="d-flex align-items-baseline">
                <p class="fs-2 fw-bold mb-0 me-2">{{ metrics.avgSyncTime }}<small>s</small></p>
              </div>
            </div>
          </div>

          <!-- Total Errors Today -->
          <div class="col-lg-3 col-md-6 col-6">
            <div class="p-3 h-100 rounded border border-light-subtle dashboard-card">
              <div class="d-flex justify-content-between mb-1">
                <h3 class="text-muted small fw-normal mb-0">Total Errors Today</h3>
                <i class="fas fa-exclamation-triangle text-danger opacity-50"></i>
              </div>
              <div class="d-flex align-items-baseline">
                <p class="fs-2 fw-bold mb-0 me-2">{{ metrics.errorCount }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Charts & Last Sync Details -->
      <section class="mb-4">
        <div class="row g-3">
          <!-- Sync Trends Charts -->
          <div class="col-lg-8">
            <div class="p-3 rounded border border-light-subtle h-100 dashboard-card">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h2 class="h6 fw-semibold mb-0">Sync Trends</h2>
                <div class="dropdown">
                  <button
                    class="btn btn-sm btn-outline-secondary dropdown-toggle"
                    type="button"
                    data-bs-toggle="dropdown"
                    v-tooltip="'Chart options'"
                  >
                    <i class="fas fa-cog"></i>
                  </button>
                  <ul class="dropdown-menu dropdown-menu-end" :class="{ 'dropdown-menu-dark': $root.theme === 'dark' }">
                    <li>
                      <a class="dropdown-item" href="#" @click.prevent="toggleComparisonData"
                        >Compare w/ Previous Period</a
                      >
                    </li>
                    <li><a class="dropdown-item" href="#" @click.prevent="changeChartType">Change Chart Type</a></li>
                    <li><hr class="dropdown-divider" /></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="exportChart">Export Chart...</a></li>
                  </ul>
                </div>
              </div>

              <div class="row g-3">
                <div class="col-md-6">
                  <h3 class="small text-muted fw-medium mb-1">Records Synced Daily</h3>
                  <div
                    class="chart-placeholder rounded bg-light-subtle d-flex align-items-center justify-content-center"
                    style="height: 250px"
                  >
                    Line Chart Placeholder
                    <p v-if="chartError" class="text-danger small mt-2">Could not load chart data.</p>
                  </div>
                </div>
                <div class="col-md-6">
                  <h3 class="small text-muted fw-medium mb-1">Status Distribution</h3>
                  <div
                    class="chart-placeholder rounded d-flex align-items-center justify-content-center bg-light-subtle"
                    style="height: 250px"
                  >
                    Pie Chart Placeholder
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Last Sync Details -->
          <div class="col-lg-4">
            <div class="p-3 rounded border border-light-subtle h-100 dashboard-card">
              <h2 class="h6 fw-semibold mb-3">Last Sync Details</h2>
              <ul class="list-unstyled mb-0 small text-muted space-y-2">
                <li class="d-flex justify-content-between align-items-center">
                  <span><i class="fas fa-clock fa-fw me-2 opacity-50"></i> Time</span>
                  <strong class="text-body">{{ syncStatus.lastSyncTime }}</strong>
                </li>
                <li class="d-flex justify-content-between align-items-center">
                  <span><i class="fas fa-cogs fa-fw me-2 opacity-50"></i> Type</span>
                  <strong class="text-body">{{ syncStatus.syncType }}</strong>
                </li>
                <li class="d-flex justify-content-between align-items-center">
                  <span><i class="fas fa-check-square fa-fw me-2 opacity-50"></i> Status</span>
                  <span :class="['badge', 'fw-medium', statusBadgeClass(syncStatus.status)]">
                    <i :class="statusIcon(syncStatus.status) + ' me-1'"></i> {{ syncStatus.status }}
                  </span>
                </li>
                <li class="d-flex justify-content-between align-items-center">
                  <span><i class="fas fa-database fa-fw me-2 opacity-50"></i> Processed</span>
                  <strong class="text-body">{{ syncStatus.recordsProcessed?.toLocaleString() }}</strong>
                </li>
                <li class="d-flex justify-content-between align-items-center">
                  <span><i class="fas fa-exclamation-circle fa-fw me-2 opacity-50"></i> Errors</span>
                  <strong :class="[syncStatus.errors > 0 ? 'text-danger' : 'text-body']">{{
                    syncStatus.errors
                  }}</strong>
                </li>
              </ul>
              <button
                class="btn btn-sm btn-outline-primary w-100 mt-3"
                @click="navigateToJobLog(syncStatus.lastJobId)"
                :disabled="!syncStatus.lastJobId"
              >
                <i class="fas fa-search me-1"></i> View Full Log for this Sync
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Recent Activity Table -->
      <section>
        <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
          <h2 class="h6 fw-semibold mb-0">Recent Activity</h2>

          <!-- Table Controls -->
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <input
              type="search"
              class="form-control form-control-sm"
              placeholder="Search logs..."
              v-model="logSearchTerm"
              style="max-width: 200px"
            />

            <!-- Column Visibility -->
            <div class="dropdown">
              <button
                class="btn btn-sm btn-outline-secondary dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
                v-tooltip="'Show/Hide Columns'"
              >
                <i class="fas fa-columns"></i>
              </button>
              <ul class="dropdown-menu dropdown-menu-end p-2" style="min-width: 200px">
                <li v-for="(label, key) in columnLabels" :key="key">
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      :id="'colCheck' + key"
                      v-model="columnVisibility[key]"
                    />
                    <label class="form-check-label small" :for="'colCheck' + key">{{ label }}</label>
                  </div>
                </li>
              </ul>
            </div>

            <!-- Density Control -->
            <div class="btn-group btn-group-sm">
              <button
                type="button"
                :class="['btn', tableDensity === 'compact' ? 'btn-secondary' : 'btn-outline-secondary']"
                @click="tableDensity = 'compact'"
                v-tooltip="'Compact View'"
              >
                <i class="fas fa-compress-alt"></i>
              </button>
              <button
                type="button"
                :class="['btn', tableDensity === 'comfortable' ? 'btn-secondary' : 'btn-outline-secondary']"
                @click="tableDensity = 'comfortable'"
                v-tooltip="'Comfortable View'"
              >
                <i class="fas fa-expand-alt"></i>
              </button>
            </div>

            <!-- Export Button -->
            <button
              class="btn btn-sm btn-outline-secondary"
              @click="exportLogs"
              v-tooltip="'Export visible logs (CSV)'"
            >
              <i class="fas fa-file-csv"></i> Export
            </button>
          </div>
        </div>

        <!-- Selection Actions Bar -->
        <div
          v-if="selectedLogs.length > 0"
          class="alert alert-secondary p-2 d-flex justify-content-between align-items-center mb-2"
        >
          <span class="small">{{ selectedLogs.length }} log(s) selected</span>
          <div>
            <button
              class="btn btn-sm btn-outline-primary me-2"
              @click="retrySelectedLogs"
              v-tooltip="'Retry selected failed syncs'"
            >
              <i class="fas fa-redo me-1"></i> Retry Selected
            </button>
            <button
              class="btn btn-sm btn-outline-danger"
              @click="archiveSelectedLogs"
              v-tooltip="'Archive selected logs'"
            >
              <i class="fas fa-archive me-1"></i> Archive Selected
            </button>
          </div>
        </div>

        <!-- Logs Table -->
        <div class="rounded border border-light-subtle overflow-hidden dashboard-card">
          <div class="table-responsive">
            <table :class="['table table-hover mb-0 small align-middle', { 'table-sm': tableDensity === 'compact' }]">
              <thead class="bg-light-subtle">
                <tr>
                  <th class="px-3 py-2" style="width: 30px">
                    <input
                      type="checkbox"
                      class="form-check-input"
                      @change="toggleSelectAllLogs($event)"
                      :checked="allFilteredLogsSelected"
                      :disabled="filteredAndSortedLogs.length === 0"
                    />
                  </th>
                  <th
                    v-if="columnVisibility.timestamp"
                    scope="col"
                    class="px-3 py-2 text-muted fw-medium text-uppercase letter-spacing-1 sortable"
                    @click="sortBy('timestamp')"
                  >
                    {{ columnLabels.timestamp }} <i :class="sortIcon('timestamp')"></i>
                  </th>
                  <th
                    v-if="columnVisibility.event"
                    scope="col"
                    class="px-3 py-2 text-muted fw-medium text-uppercase letter-spacing-1"
                  >
                    {{ columnLabels.event }}
                  </th>
                  <th
                    v-if="columnVisibility.status"
                    scope="col"
                    class="px-3 py-2 text-muted fw-medium text-uppercase letter-spacing-1 text-center sortable"
                    @click="sortBy('status')"
                  >
                    {{ columnLabels.status }} <i :class="sortIcon('status')"></i>
                  </th>
                  <th
                    v-if="columnVisibility.jobId"
                    scope="col"
                    class="px-3 py-2 text-muted fw-medium text-uppercase letter-spacing-1"
                  >
                    {{ columnLabels.jobId }}
                  </th>
                  <th
                    v-if="columnVisibility.duration"
                    scope="col"
                    class="px-3 py-2 text-muted fw-medium text-uppercase letter-spacing-1 sortable text-end"
                    @click="sortBy('duration')"
                  >
                    {{ columnLabels.duration }} <i :class="sortIcon('duration')"></i>
                  </th>
                  <th
                    v-if="columnVisibility.records"
                    scope="col"
                    class="px-3 py-2 text-muted fw-medium text-uppercase letter-spacing-1 sortable text-end"
                    @click="sortBy('records')"
                  >
                    {{ columnLabels.records }} <i :class="sortIcon('records')"></i>
                  </th>
                  <th
                    v-if="columnVisibility.actions"
                    scope="col"
                    class="px-3 py-2 text-muted fw-medium text-uppercase letter-spacing-1 text-center"
                  >
                    {{ columnLabels.actions }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <!-- Empty State -->
                <tr v-if="filteredAndSortedLogs.length === 0 && !isLoading">
                  <td :colspan="visibleColumnCount" class="text-center py-5 text-muted fst-italic">
                    <i class="fas fa-list-alt fs-4 d-block mb-2 opacity-50"></i>
                    No activity logs found matching your criteria.<br />
                    <a href="#" @click.prevent="resetFilters" class="link-primary small">Reset Filters?</a>
                  </td>
                </tr>

                <!-- Log Rows -->
                <tr v-for="log in paginatedLogs" :key="log.id">
                  <td class="px-3 py-2">
                    <input type="checkbox" class="form-check-input" :value="log.id" v-model="selectedLogs" />
                  </td>
                  <td v-if="columnVisibility.timestamp" class="px-3 py-2 text-muted">{{ log.timestamp }}</td>
                  <td v-if="columnVisibility.event" class="px-3 py-2 text-body">{{ log.message }}</td>
                  <td v-if="columnVisibility.status" class="px-3 py-2 text-center">
                    <span :class="['badge', 'fw-medium', statusBadgeClass(log.status)]">
                      <i :class="statusIcon(log.status) + ' me-1'"></i>{{ log.status }}
                    </span>
                  </td>
                  <td v-if="columnVisibility.jobId" class="px-3 py-2 text-muted font-monospace x-small">
                    {{ log.jobId }}
                  </td>
                  <td v-if="columnVisibility.duration" class="px-3 py-2 text-muted text-end">{{ log.duration }}</td>
                  <td v-if="columnVisibility.records" class="px-3 py-2 text-muted text-end">
                    {{ log.records?.toLocaleString() }}
                  </td>
                  <td v-if="columnVisibility.actions" class="px-3 py-2 text-center">
                    <button
                      class="btn btn-xs btn-outline-secondary me-1"
                      @click="viewLogDetails(log.id)"
                      v-tooltip="'View Details'"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                    <button
                      v-if="log.status === 'error' || log.status === 'failed'"
                      class="btn btn-xs btn-outline-warning"
                      @click="retryLog(log.id)"
                      v-tooltip="'Retry Sync'"
                    >
                      <i class="fas fa-redo"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <nav
            v-if="totalPages > 1"
            aria-label="Log pagination"
            class="p-2 border-top d-flex justify-content-between align-items-center bg-light-subtle"
          >
            <div class="small text-muted">
              Page {{ currentPage }} of {{ totalPages }} ({{ filteredLogs.length }} items)
            </div>
            <ul class="pagination pagination-sm justify-content-end mb-0">
              <li :class="['page-item', { disabled: currentPage === 1 }]">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)" aria-label="Previous">
                  <span aria-hidden="true">&laquo;</span>
                </a>
              </li>
              <li
                v-for="page in paginationRange"
                :key="page"
                :class="['page-item', { active: page === currentPage, disabled: page === '...' }]"
              >
                <span v-if="page === '...'" class="page-link">...</span>
                <a v-else class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
              </li>
              <li :class="['page-item', { disabled: currentPage === totalPages }]">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)" aria-label="Next">
                  <span aria-hidden="true">&raquo;</span>
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </section>
    </div>
  </main>
</template>

<script>
import { Tooltip } from 'bootstrap'

// Helper to generate recent timestamps relative to now
const generateTimestamp = (minutesAgo) => {
  const now = new Date('2025-04-08T12:54:00+03:00')
  const timestamp = new Date(now.getTime() - minutesAgo * 60000)
  return timestamp.toLocaleString([], {
    year: '2-digit',
    month: 'numeric',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

export default {
  name: 'DashboardView',
  data() {
    return {
      // Core State
      isLoading: true,
      isSyncing: false,
      message: 'Initializing...',
      chartError: false,

      // Placeholder Data
      syncStatus: {},
      metrics: {},
      logs: [],

      // UI State & Filters
      filters: {},
      logSearchTerm: '',
      selectedLogs: [],
      tableDensity: 'comfortable',
      columnVisibility: {
        timestamp: true,
        event: true,
        status: true,
        jobId: false,
        duration: false,
        records: false,
        actions: true,
      },
      columnLabels: {
        timestamp: 'Timestamp',
        event: 'Event',
        status: 'Status',
        jobId: 'Job ID',
        duration: 'Duration',
        records: 'Records',
        actions: 'Actions',
      },

      // Sorting & Pagination
      sortKey: 'timestamp',
      sortDir: 'desc',
      currentPage: 1,
      itemsPerPage: 10,

      // Sync Progress
      syncProgress: { step: null, totalSteps: null, message: '', etr: '' },
    }
  },
  computed: {
    // Trend Computed Properties
    syncTrendIcon() {
      return this.metrics.trend?.syncs > 0
        ? 'fa-arrow-up'
        : this.metrics.trend?.syncs < 0
        ? 'fa-arrow-down'
        : 'fa-minus'
    },
    syncTrendClass() {
      const trend = this.metrics.trend?.syncs
      if (trend > 0) return 'bg-success-subtle text-success-emphasis'
      if (trend < 0) return 'bg-danger-subtle text-danger-emphasis'
      return 'bg-secondary-subtle text-secondary-emphasis'
    },
    syncTrendValue() {
      return Math.abs(this.metrics.trend?.syncs || 0) + '%'
    },

    // Filtered & Sorted Logs
    filteredLogs() {
      if (!this.logs) return []
      let tempLogs = this.logs

      // Apply search term filter
      if (this.logSearchTerm) {
        const searchTerm = this.logSearchTerm.toLowerCase()
        tempLogs = tempLogs.filter(
          (log) =>
            log.message.toLowerCase().includes(searchTerm) ||
            (log.id && log.id.toString().toLowerCase().includes(searchTerm)) ||
            (log.jobId && log.jobId.toString().toLowerCase().includes(searchTerm))
        )
      }

      // Apply status filter
      if (this.filters.status) {
        tempLogs = tempLogs.filter((log) => log.status.toLowerCase() === this.filters.status.toLowerCase())
      }

      return tempLogs
    },

    filteredAndSortedLogs() {
      let tempLogs = [...this.filteredLogs]

      if (this.sortKey) {
        tempLogs.sort((a, b) => {
          let valA = a[this.sortKey]
          let valB = b[this.sortKey]

          // Handle specific types for proper sorting
          if (this.sortKey === 'timestamp') {
            valA = new Date(a.timestamp)
            valB = new Date(b.timestamp)
            if (isNaN(valA) || isNaN(valB)) {
              valA = a.timestamp
              valB = b.timestamp
            }
          } else if (this.sortKey === 'duration') {
            valA = parseFloat(valA) || 0
            valB = parseFloat(valB) || 0
          } else if (this.sortKey === 'records') {
            valA = valA || 0
            valB = valB || 0
          }

          let comparison = 0
          if (valA > valB) {
            comparison = 1
          } else if (valA < valB) {
            comparison = -1
          }
          return this.sortDir === 'asc' ? comparison : comparison * -1
        })
      }
      return tempLogs
    },

    // Pagination
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.itemsPerPage)
    },

    paginatedLogs() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredAndSortedLogs.slice(start, end)
    },

    paginationRange() {
      const range = []
      const total = this.totalPages
      const current = this.currentPage
      const delta = 1
      const pagesToShow = delta * 2 + 1

      if (total <= pagesToShow + 2) {
        for (let i = 1; i <= total; i++) {
          range.push(i)
        }
      } else {
        range.push(1)

        let start = Math.max(2, current - delta)
        let end = Math.min(total - 1, current + delta)

        if (start > 2) {
          range.push('...')
        }

        for (let i = start; i <= end; i++) {
          range.push(i)
        }

        if (end < total - 1) {
          range.push('...')
        }

        range.push(total)
      }
      return range
    },

    // Table Helpers
    visibleColumnCount() {
      return Object.values(this.columnVisibility).filter(Boolean).length + 1
    },

    allFilteredLogsSelected() {
      const filteredIds = new Set(this.filteredLogs.map((log) => log.id))
      if (filteredIds.size === 0) return false
      return this.selectedLogs.length >= filteredIds.size && this.selectedLogs.every((id) => filteredIds.has(id))
    },
  },
  methods: {
    async initialLoad() {
      this.isLoading = true
      await new Promise((resolve) => setTimeout(resolve, 600))

      // Assign Placeholders
      this.syncStatus = {
        lastSyncTime: generateTimestamp(5),
        syncType: 'Two-Way Sync',
        status: 'Success',
        recordsProcessed: 185,
        errors: 2,
        lastJobId: 'sync-job-a8b3c1d9',
      }

      this.metrics = {
        totalSyncsToday: 12,
        successRate: 83,
        avgSyncTime: 11.5,
        errorCount: 15,
        trend: { syncs: 5, success: -2, time: 10, errors: 15 },
      }

      this.logs = [
        {
          id: 'log-a8b3',
          timestamp: generateTimestamp(5),
          message: 'Two-way sync completed with 2 errors.',
          status: 'success',
          jobId: 'sync-job-a8b3c1d9',
          duration: '11.2s',
          records: 185,
        },
        {
          id: 'log-a8b2',
          timestamp: generateTimestamp(37),
          message: 'Manual data upload to Freshworks.',
          status: 'success',
          jobId: 'sync-job-a8b2c1d8',
          duration: '5.7s',
          records: 89,
        },
        {
          id: 'log-a8b1',
          timestamp: generateTimestamp(120),
          message: 'Scheduled two-way sync.',
          status: 'success',
          jobId: 'sync-job-a8b1c1d7',
          duration: '12.3s',
          records: 210,
        },
        {
          id: 'log-a8a9',
          timestamp: generateTimestamp(245),
          message: 'API sync operation failed - connection timeout.',
          status: 'error',
          jobId: 'sync-job-a8a9c1d6',
          duration: '30.0s',
          records: 0,
        },
        {
          id: 'log-a8a8',
          timestamp: generateTimestamp(360),
          message: 'MySQL connection error during data extraction.',
          status: 'error',
          jobId: 'sync-job-a8a8c1d5',
          duration: '2.1s',
          records: 0,
        },
        {
          id: 'log-a8a7',
          timestamp: generateTimestamp(480),
          message: 'Scheduled two-way sync.',
          status: 'success',
          jobId: 'sync-job-a8a7c1d4',
          duration: '10.5s',
          records: 193,
        },
        {
          id: 'log-a8a6',
          timestamp: generateTimestamp(600),
          message: 'Manual data upload to Freshworks.',
          status: 'partial',
          jobId: 'sync-job-a8a6c1d3',
          duration: '8.9s',
          records: 156,
        },
        {
          id: 'log-a8a5',
          timestamp: generateTimestamp(720),
          message: 'API rate limit exceeded during operation.',
          status: 'warning',
          jobId: 'sync-job-a8a5c1d2',
          duration: '15.3s',
          records: 120,
        },
        {
          id: 'log-a8a4',
          timestamp: generateTimestamp(840),
          message: 'Scheduled two-way sync.',
          status: 'success',
          jobId: 'sync-job-a8a4c1d1',
          duration: '11.0s',
          records: 178,
        },
        {
          id: 'log-a8a3',
          timestamp: generateTimestamp(960),
          message: 'Data validation failure during import.',
          status: 'failed',
          jobId: 'sync-job-a8a3c1d0',
          duration: '5.2s',
          records: 45,
        },
        {
          id: 'log-a8a2',
          timestamp: generateTimestamp(1080),
          message: 'Scheduled two-way sync.',
          status: 'success',
          jobId: 'sync-job-a8a2c1c9',
          duration: '11.7s',
          records: 201,
        },
        {
          id: 'log-a8a1',
          timestamp: generateTimestamp(1200),
          message: 'Manual data upload to Freshworks.',
          status: 'success',
          jobId: 'sync-job-a8a1c1c8',
          duration: '6.8s',
          records: 92,
        },
      ]

      this.isLoading = false
      this.message = 'Data loaded successfully.'
    },

    // Sync Controls
    triggerBulkUpload() {
      this.startSyncOperation('Bulk Upload', 3)
    },

    triggerTwoWaySync() {
      this.startSyncOperation('Two-Way Sync', 5)
    },

    async startSyncOperation(type, steps) {
      this.isSyncing = true
      this.message = `Running ${type}...`
      this.syncProgress = { step: 1, totalSteps: steps, message: 'Initializing sync', etr: '2 min' }

      const stepMessages = [
        'Initializing sync',
        'Connecting to databases',
        'Extracting data from MySQL',
        'Processing data transformations',
        'Uploading to Freshworks API',
        'Reconciling differences',
        'Finalizing sync operation',
      ]

      // Simulate progress
      for (let i = 1; i <= steps; i++) {
        this.syncProgress.step = i
        this.syncProgress.message = stepMessages[i - 1]
        this.syncProgress.etr = `${Math.round(((steps - i + 1) * 40) / 60)} min ${((steps - i + 1) * 40) % 60} sec`

        await new Promise((resolve) => setTimeout(resolve, 1000))
      }

      // Complete operation
      this.syncStatus = {
        lastSyncTime: generateTimestamp(0),
        syncType: type,
        status: 'Success',
        recordsProcessed: Math.floor(Math.random() * 100) + 100,
        errors: Math.floor(Math.random() * 3),
        lastJobId: `sync-job-${Math.random().toString(36).substring(2, 10)}`,
      }

      // Add new log entry
      const newLog = {
        id: `log-${Math.random().toString(36).substring(2, 6)}`,
        timestamp: generateTimestamp(0),
        message: `${type} completed successfully.`,
        status: 'success',
        jobId: this.syncStatus.lastJobId,
        duration: `${(Math.random() * 10 + 5).toFixed(1)}s`,
        records: this.syncStatus.recordsProcessed,
      }

      this.logs.unshift(newLog)

      this.isSyncing = false
      this.message = `${type} completed successfully.`
      this.syncProgress = { step: null, totalSteps: null, message: '', etr: '' }
    },

    refreshData() {
      this.message = 'Refreshing data...'
      this.initialLoad()
    },

    // Table Controls
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortKey = key
        this.sortDir = 'desc'
      }
    },

    sortIcon(column) {
      if (this.sortKey !== column) return 'fas fa-sort text-muted opacity-50'
      return this.sortDir === 'asc' ? 'fas fa-sort-up ms-1' : 'fas fa-sort-down ms-1'
    },

    changePage(page) {
      if (page < 1 || page > this.totalPages) return
      this.currentPage = page
    },

    resetFilters() {
      this.filters = {}
      this.logSearchTerm = ''
      this.currentPage = 1
    },

    toggleSelectAllLogs(event) {
      if (event.target.checked) {
        this.selectedLogs = this.filteredAndSortedLogs.map((log) => log.id)
      } else {
        this.selectedLogs = []
      }
    },

    // Log Actions
    viewLogDetails(logId) {
      const log = this.logs.find((l) => l.id === logId)
      if (!log) return

      alert(
        `Log Details for ${log.jobId}\n\nTime: ${log.timestamp}\nStatus: ${log.status}\nMessage: ${log.message}\nDuration: ${log.duration}\nRecords: ${log.records}`
      )
    },

    retryLog(logId) {
      const log = this.logs.find((l) => l.id === logId)
      if (!log) return

      this.message = `Retrying failed job ${log.jobId}...`
      setTimeout(() => {
        const updatedLog = {
          ...log,
          status: Math.random() > 0.7 ? 'success' : 'partial',
          timestamp: generateTimestamp(0),
          message: `Retry of job ${log.jobId}: ${Math.random() > 0.7 ? 'Successful' : 'Partially completed'}`,
        }

        const index = this.logs.findIndex((l) => l.id === logId)
        if (index !== -1) {
          this.logs.splice(index, 1, updatedLog)
        }

        this.message = 'Retry completed.'
      }, 1500)
    },

    retrySelectedLogs() {
      if (this.selectedLogs.length === 0) return

      this.message = `Retrying ${this.selectedLogs.length} failed operations...`
      setTimeout(() => {
        this.selectedLogs.forEach((logId) => {
          const index = this.logs.findIndex((l) => l.id === logId)
          if (index !== -1) {
            this.logs[index] = {
              ...this.logs[index],
              status: Math.random() > 0.7 ? 'success' : 'partial',
              timestamp: generateTimestamp(0),
              message: `Retry of job ${this.logs[index].jobId}: ${
                Math.random() > 0.7 ? 'Successful' : 'Partially completed'
              }`,
            }
          }
        })

        this.message = 'Batch retry completed.'
        this.selectedLogs = []
      }, 2500)
    },

    archiveSelectedLogs() {
      if (this.selectedLogs.length === 0) return

      const count = this.selectedLogs.length
      this.message = `Archiving ${count} logs...`

      setTimeout(() => {
        this.logs = this.logs.filter((log) => !this.selectedLogs.includes(log.id))
        this.selectedLogs = []
        this.message = `${count} logs archived successfully.`
      }, 1000)
    },

    // Chart Controls
    toggleComparisonData() {
      // In a real application, this would update the chart data
      alert('This would toggle the comparison data in the charts')
    },

    changeChartType() {
      // In a real application, this would change the chart type
      alert('This would switch between line/bar/area chart types')
    },

    exportChart() {
      // In a real application, this would export the chart
      alert('This would export the chart as PNG/PDF/SVG')
    },

    // Export Function
    exportLogs() {
      // In a real application, this would generate and download a CSV file
      alert(`This would export ${this.filteredLogs.length} logs to CSV format`)
    },

    // Navigation
    navigateToJobLog(jobId) {
      // In a real application, this would navigate to the job log detail page
      alert(`Navigating to job log detail for ${jobId}`)
    },

    // Status Helpers
    statusIcon(status) {
      if (!status) return 'fas fa-question-circle'

      status = status.toLowerCase()
      if (status === 'success') return 'fas fa-check-circle'
      if (status === 'error' || status === 'failed') return 'fas fa-times-circle'
      if (status === 'warning' || status === 'partial') return 'fas fa-exclamation-triangle'
      if (status === 'pending') return 'fas fa-clock'
      return 'fas fa-info-circle'
    },

    statusClass(status) {
      if (!status) return 'text-muted'

      status = status.toLowerCase()
      if (status === 'success') return 'text-success'
      if (status === 'error' || status === 'failed') return 'text-danger'
      if (status === 'warning' || status === 'partial') return 'text-warning'
      if (status === 'pending') return 'text-info'
      return 'text-muted'
    },

    statusBadgeClass(status) {
      if (!status) return 'bg-secondary'

      status = status.toLowerCase()
      if (status === 'success') return 'bg-success-subtle text-success'
      if (status === 'error' || status === 'failed') return 'bg-danger-subtle text-danger'
      if (status === 'warning') return 'bg-warning-subtle text-warning-emphasis'
      if (status === 'partial') return 'bg-warning-subtle text-warning-emphasis'
      if (status === 'pending') return 'bg-info-subtle text-info-emphasis'
      return 'bg-secondary-subtle text-secondary-emphasis'
    },
  },
  mounted() {
    this.initialLoad()

    // Initialize tooltips
    this.$nextTick(() => {
      document.querySelectorAll('[data-bs-toggle="tooltip"], [v-tooltip]').forEach((el) => {
        new Tooltip(el, {
          placement: 'auto',
          boundary: document.body,
        })
      })
    })
  },
  directives: {
    tooltip: {
      mounted(el, binding) {
        new Tooltip(el, {
          title: binding.value,
          placement: 'auto',
          boundary: document.body,
        })
      },
      updated(el, binding) {
        if (el._tooltip) {
          el._tooltip.dispose()
        }
        new Tooltip(el, {
          title: binding.value,
          placement: 'auto',
          boundary: document.body,
        })
      },
      unmounted(el) {
        if (el._tooltip) {
          el._tooltip.dispose()
        }
      },
    },
  },
}
</script>

<style scoped>
/* Add styles for dashboard cards for theme adaptation */
.dashboard-card {
  background-color: var(--bs-body-bg); /* Use Bootstrap variable */
  /* Add transitions for hover effects if desired */
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.dashboard-card:hover {
  /* transform: translateY(-3px); */ /* Subtle lift */
  /* box-shadow: var(--bs-box-shadow-sm); */ /* Subtle shadow */
}

/* Styles for sortable table headers */
.sortable {
  cursor: pointer;
  user-select: none; /* Prevent text selection on click */
}
.sortable:hover {
  color: var(--bs-primary) !important; /* Use primary color on hover */
}
.sortable i {
  /* Sort icon */
  font-size: 0.8em;
  margin-left: 0.3em;
}

/* Specific styles for dashboard elements if needed */
.chart-placeholder {
  min-height: 250px; /* Ensure charts have space */
  display: flex;
  align-items: center;
  justify-content: center;
  /* background-color: var(--bs-light-bg-subtle); /* Use variable */
  /* border: 1px dashed var(--bs-border-color-translucent); */ /* Remove dashed border */
  text-align: center;
  font-style: italic;
  color: var(--bs-secondary-color); /* Use variable */
  font-size: 0.9em;
  padding: 1rem;
}

/* Skeleton loader styles from previous example */
.skeleton-box {
  background-color: var(--bs-secondary-bg);
  border-radius: 0.375rem;
  animation: pulse-bg 1.5s infinite ease-in-out;
}
@keyframes pulse-bg {
  0% {
    background-color: var(--bs-secondary-bg);
  }
  50% {
    background-color: var(--bs-tertiary-bg);
  }
  100% {
    background-color: var(--bs-secondary-bg);
  }
}
[data-bs-theme='dark'] .skeleton-box {
  background-color: var(--bs-secondary);
  animation: pulse-bg-dark 1.5s infinite ease-in-out;
}
@keyframes pulse-bg-dark {
  0% {
    background-color: var(--bs-secondary);
  }
  50% {
    background-color: var(--bs-dark-bg-subtle);
  }
  100% {
    background-color: var(--bs-secondary);
  }
}
.space-y-2 > li:not(:last-child) {
  margin-bottom: 0.75rem;
}
.letter-spacing-1 {
  letter-spacing: 1px;
}
.btn-xs {
  padding: 0.1rem 0.3rem;
  font-size: 0.7rem;
}
.x-small {
  font-size: 0.75em;
}
.font-monospace {
  font-family: var(--bs-font-monospace);
}
</style>
