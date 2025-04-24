// DocHistoryView.vue
<template>
  <div class="container-fluid p-4">
    <h2 class="mb-4">Document History</h2>
    <p class="text-muted mb-4">View past document requests.</p>

    <div class="card mb-4 p-3">
      <h3 class="h6 mb-2">Filters</h3>
      <div class="d-flex gap-2 flex-wrap">
        <select class="form-select form-select-sm" v-model="filters.docType">
          <option value="">All Types</option>
          <option v-for="type in docTypes" :key="type" :value="type">{{ type }}</option>
        </select>
        <select class="form-select form-select-sm" v-model="filters.status">
          <option value="">All Status</option>
          <option v-for="status in statuses" :key="status" :value="status">{{ status }}</option>
        </select>
        <input type="date" class="form-control form-control-sm" v-model="filters.date" />
        <button class="btn btn-secondary btn-sm" @click="resetFilters">Reset</button>
      </div>
    </div>

    <div class="card">
      <table class="table mb-0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Time</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in filteredRequests" :key="r.id">
            <td>{{ r.id }}</td>
            <td>{{ r.docType }}</td>
            <td>{{ r.timestamp }}</td>
            <td>
              <span :class="['badge', badgeClass(r.status)]">{{ r.status }}</span>
            </td>
            <td>
              <button
                class="btn btn-sm btn-outline-primary me-1"
                @click="viewDetails(r)"
                :disabled="r.status === 'Pending'"
              >
                View
              </button>
              <button v-if="r.status === 'Success'" class="btn btn-sm btn-success" @click="download(r)">
                Download
              </button>
            </td>
          </tr>
          <tr v-if="!filteredRequests.length">
            <td colspan="5" class="text-center p-4 text-muted">No records.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const docTypes = ['Quote', 'Invoice', 'LPO', 'Contract']
const statuses = ['Success', 'Failed', 'Pending']
const generationRequests = ref([
  { id: '1', docType: 'Quote', timestamp: '04/24/25, 10:00 AM', status: 'Success' },
  { id: '2', docType: 'Invoice', timestamp: '04/24/25, 09:00 AM', status: 'Failed' },
  { id: '3', docType: 'Contract', timestamp: '04/24/25, 08:30 AM', status: 'Pending' },
])
const filters = ref({ docType: '', status: '', date: '' })

const filteredRequests = computed(() => {
  return generationRequests.value.filter((r) => {
    return (
      (!filters.value.docType || r.docType === filters.value.docType) &&
      (!filters.value.status || r.status === filters.value.status) &&
      (!filters.value.date || r.timestamp.startsWith(filters.value.date))
    )
  })
})

function viewDetails(r) {
  alert(JSON.stringify(r, null, 2))
}
function download(r) {
  alert(`Downloading ${r.id}`)
}
function resetFilters() {
  filters.value = { docType: '', status: '', date: '' }
}
function badgeClass(s) {
  return s === 'Success' ? 'bg-success-subtle' : s === 'Failed' ? 'bg-danger-subtle' : 'bg-warning-subtle'
}
</script>

<style scoped></style>
