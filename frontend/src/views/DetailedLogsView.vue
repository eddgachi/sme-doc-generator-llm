<template>
  <div>
    <h2 class="mb-4">Detailed Logs {{ jobId ? 'for Job ' + jobId : '' }}</h2>
    <p class="text-muted mb-4">Search, filter, and view all system activity logs.</p>
    <div class="card mb-4">
      <div class="card-body">
        <p class="text-muted small">Filtering options placeholder...</p>
      </div>
    </div>

    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Level</th>
                <th>Job ID</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in detailedLogs" :key="log.id">
                <td>
                  <small>{{ log.timestamp }}</small>
                </td>
                <td>
                  <span :class="['badge', levelBadgeClass(log.level)]">{{ log.level }}</span>
                </td>
                <td>
                  <small>{{ log.jobId || 'N/A' }}</small>
                </td>
                <td>{{ log.message }}</td>
              </tr>
              <tr v-if="detailedLogs.length === 0">
                <td colspan="4" class="text-center p-5 text-muted">No logs found matching criteria.</td>
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
  name: 'DetailedLogsView',
  props: {
    jobId: {
      // Passed from router if path is /logs/:jobId
      type: String,
      default: null,
    },
  },
  data() {
    return {
      detailedLogs: [
        // Sample data - would be fetched based on filters/jobId
        {
          id: 'detail-1',
          timestamp: generateTimestamp(5),
          level: 'INFO',
          jobId: 'sync-job-a8b3c1d9',
          message: 'Processed record Contact:001 successfully.',
        },
        {
          id: 'detail-2',
          timestamp: generateTimestamp(5),
          level: 'WARN',
          jobId: 'sync-job-a8b3c1d9',
          message: "Record Account:A005 skipped, missing required field 'industry'.",
        },
        {
          id: 'detail-3',
          timestamp: generateTimestamp(5),
          level: 'ERROR',
          jobId: 'sync-job-a8b3c1d9',
          message: 'Failed to update record Deal:D999 - API Error 400 Bad Request.',
        },
        {
          id: 'detail-4',
          timestamp: generateTimestamp(6),
          level: 'INFO',
          jobId: 'sync-job-a8b3c1d9',
          message: 'Target update phase started.',
        },
        {
          id: 'detail-5',
          timestamp: generateTimestamp(35),
          level: 'ERROR',
          jobId: 'bulk-job-f4e1b2a0',
          message: 'Connection to https://nakuru-crm.freshworks.com timed out after 30000ms',
        },
        {
          id: 'detail-6',
          timestamp: generateTimestamp(35),
          level: 'FATAL',
          jobId: 'bulk-job-f4e1b2a0',
          message: 'Aborting sync job due to critical connection failure.',
        },
        // ... more logs
      ],
    }
  },
  watch: {
    jobId(newJobId) {
      console.log('Job ID prop changed:', newJobId)
      // Refetch logs if the route param changes
      // this.fetchLogs();
    },
  },
  methods: {
    // Placeholder for level badge class
    levelBadgeClass(level) {
      level = level?.toLowerCase()
      if (level === 'error' || level === 'fatal') return 'bg-danger text-white'
      if (level === 'warn') return 'bg-warning text-dark'
      if (level === 'info') return 'bg-info text-dark'
      if (level === 'debug') return 'bg-secondary text-white'
      return 'bg-light text-dark'
    },
  },
  mounted() {
    console.log('DetailedLogsView mounted with Job ID:', this.jobId)
    // Fetch initial logs based on potential jobId prop or default filters
    // this.fetchLogs();
  },
}
</script>
