<template>
  <div>
    <h2 class="mb-4">Sync History</h2>
    <p class="text-muted mb-4">List of all past synchronization jobs.</p>
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Type</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Duration</th>
                <th>Status</th>
                <th>Records</th>
                <th>Errors</th>
                <th>Triggered By</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="job in historyJobs" :key="job.id">
                <td>
                  <small>{{ job.id }}</small>
                </td>
                <td>{{ job.type }}</td>
                <td>{{ job.startTime }}</td>
                <td>{{ job.endTime }}</td>
                <td>{{ job.duration }}</td>
                <td>
                  <span :class="['badge', statusBadgeClass(job.status)]">{{ job.status }}</span>
                </td>
                <td>{{ job.records }}</td>
                <td>{{ job.errors }}</td>
                <td>{{ job.triggeredBy }}</td>
                <td>
                  <router-link :to="'/logs/' + job.id" class="btn btn-sm btn-outline-primary" v-tooltip="'View Logs'">
                    <i class="fas fa-clipboard-list"></i>
                  </router-link>
                </td>
              </tr>
              <tr v-if="historyJobs.length === 0">
                <td colspan="10" class="text-center p-5 text-muted">No history found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Helper to generate recent timestamps relative to now
const generateTimestamp = (minutesAgo) => {
  /* ... same helper ... */
}

export default {
  name: 'HistoryView',
  data() {
    return {
      historyJobs: [
        {
          id: 'sync-job-a8b3c1d9',
          type: 'Two-Way',
          startTime: generateTimestamp(7),
          endTime: generateTimestamp(5),
          duration: '18s',
          status: 'Success',
          records: 185,
          errors: 2,
          triggeredBy: 'admin',
        },
        {
          id: 'bulk-job-f4e1b2a0',
          type: 'Bulk Upload',
          startTime: generateTimestamp(36),
          endTime: generateTimestamp(35),
          duration: '35s',
          status: 'Error',
          records: 0,
          errors: 1,
          triggeredBy: 'Schedule',
        },
        {
          id: 'sync-job-c2d9e8f7',
          type: 'Two-Way',
          startTime: generateTimestamp(66),
          endTime: generateTimestamp(65),
          duration: '12s',
          status: 'Success',
          records: 95,
          errors: 0,
          triggeredBy: 'Schedule',
        },
        {
          id: 'bulk-job-b1a5c6d7',
          type: 'Bulk Upload',
          startTime: generateTimestamp(127),
          endTime: generateTimestamp(125),
          duration: '45s',
          status: 'Success',
          records: 1520,
          errors: 0,
          triggeredBy: 'jane.doe',
        },
        {
          id: 'sync-job-z9y3x2w1',
          type: 'Two-Way',
          startTime: generateTimestamp(185),
          endTime: generateTimestamp(185) + '(failed)',
          duration: '5s',
          status: 'Error',
          records: 0,
          errors: 1,
          triggeredBy: 'Schedule',
        },
        // ... more jobs
      ],
    }
  },
  methods: {
    // Placeholder for status badge class - could be imported from a utility file
    statusBadgeClass(status) {
      switch (status?.toLowerCase()) {
        case 'success':
          return 'bg-success-subtle text-success-emphasis border border-success-subtle'
        case 'failed':
        case 'error':
          return 'bg-danger-subtle text-danger-emphasis border border-danger-subtle'
        case 'in progress':
        case 'pending':
          return 'bg-warning-subtle text-warning-emphasis border border-warning-subtle'
        default:
          return 'bg-secondary-subtle text-secondary-emphasis border border-secondary-subtle'
      }
    },
  },
}
</script>
