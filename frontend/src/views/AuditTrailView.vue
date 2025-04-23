<template>
  <div>
    <h2 class="mb-4">Audit Trail</h2>
    <p class="text-muted mb-4">Record of user actions performed in the system.</p>
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User</th>
                <th>Action</th>
                <th>Details</th>
                <th>IP Address</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in auditLog" :key="entry.id">
                <td>
                  <small>{{ entry.timestamp }}</small>
                </td>
                <td>{{ entry.user }}</td>
                <td>{{ entry.action }}</td>
                <td>
                  <small>{{ entry.details }}</small>
                </td>
                <td>{{ entry.ipAddress }}</td>
              </tr>
              <tr v-if="auditLog.length === 0">
                <td colspan="5" class="text-center p-5 text-muted">No audit records found.</td>
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
  name: 'AuditTrailView',
  data() {
    return {
      auditLog: [
        {
          id: 'audit-1',
          timestamp: generateTimestamp(7),
          user: 'admin',
          action: 'Manual Sync Triggered',
          details: 'Type: Two-Way, Job ID: sync-job-a8b3c1d9',
          ipAddress: '192.168.1.10',
        },
        {
          id: 'audit-2',
          timestamp: generateTimestamp(20),
          user: 'admin',
          action: 'Configuration Updated',
          details: 'Updated Freshworks API Key',
          ipAddress: '192.168.1.10',
        },
        {
          id: 'audit-3',
          timestamp: generateTimestamp(127),
          user: 'jane.doe',
          action: 'Manual Sync Triggered',
          details: 'Type: Bulk Upload, Job ID: bulk-job-b1a5c6d7',
          ipAddress: '10.0.5.25',
        },
        {
          id: 'audit-4',
          timestamp: generateTimestamp(190),
          user: 'system',
          action: 'User Logged In',
          details: 'User: jane.doe',
          ipAddress: '10.0.5.25',
        },
        // ... more entries
      ],
    }
  },
}
</script>
