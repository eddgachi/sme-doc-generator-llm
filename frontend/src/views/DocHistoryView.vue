<template>
  <div class="container-fluid p-4">
    <h2 class="mb-4">Document History</h2>
    <p class="text-muted mb-4">View past document requests.</p>

    <div class="card mb-4 p-3">
      <h3 class="h6 mb-2">Filters</h3>
      <div class="d-flex gap-2 flex-wrap">
        <select class="form-select form-select-sm" v-model="filters.docType">
          <option value="">All Types</option>
          <option v-for="type in uniqueDocTypes" :key="type" :value="type">{{ type }}</option>
        </select>
        <button class="btn btn-secondary btn-sm" @click="resetFilters">Reset</button>
      </div>
    </div>

    <div class="card">
      <div v-if="loadingHistory" class="text-center p-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading History...</span>
        </div>
        <p class="mt-2">Loading history...</p>
      </div>
      <div v-else-if="historyError" class="alert alert-danger m-3"><strong>Error:</strong> {{ historyError }}</div>
      <div v-else class="card-body p-0">
        <table class="table mb-0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Template Name</th>
              <th>Type</th>
              <th>Generated At</th>
              <th>Format</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in filteredHistory" :key="record.id">
              <td>{{ record.id.substring(0, 8) }}...</td>
              <td>{{ getTemplateName(record.template_id) || 'Unknown Template' }}</td>
              <td>{{ getTemplateDocType(record.template_id) || 'N/A' }}</td>
              <td>{{ formatDate(record.generated_at) }}</td>
              <td>{{ record.document_format ? record.document_format.toUpperCase() : 'N/A' }}</td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-1" @click="viewDetails(record.id)">
                  View Details
                </button>
              </td>
            </tr>
            <tr v-if="filteredHistory.length === 0 && !loadingHistory && !historyError">
              <td colspan="6" class="text-center p-4 text-muted">No history records found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div
      class="modal fade"
      id="historyDetailModal"
      tabindex="-1"
      aria-labelledby="historyDetailModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="historyDetailModalLabel">History Record Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="selectedRecordDetails">
            <h6>Record ID: {{ selectedRecordDetails.id }}</h6>
            <p>
              <strong>Template:</strong> {{ getTemplateName(selectedRecordDetails.template_id) || 'Unknown' }} ({{
                getTemplateDocType(selectedRecordDetails.template_id) || 'N/A'
              }})
            </p>
            <p><strong>Generated At:</strong> {{ formatDate(selectedRecordDetails.generated_at) }}</p>
            <p>
              <strong>Format Requested:</strong>
              {{ selectedRecordDetails.document_format ? selectedRecordDetails.document_format.toUpperCase() : 'N/A' }}
            </p>

            <h6 class="mt-3">Input Data:</h6>
            <pre class="border p-2 rounded bg-light-subtle small">{{
              formatInputData(selectedRecordDetails.input_data)
            }}</pre>

            <h6 class="mt-3">Generated Content:</h6>
            <pre class="border p-2 rounded bg-light-subtle small">{{ selectedRecordDetails.generated_content }}</pre>
          </div>
          <div class="modal-body" v-else-if="loadingDetails">
            <div class="text-center">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading Details...</span>
              </div>
              <p class="mt-2">Loading details...</p>
            </div>
          </div>
          <div class="modal-body" v-else-if="detailsError">
            <div class="alert alert-danger"><strong>Error:</strong> {{ detailsError }}</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Modal } from 'bootstrap' // Import Bootstrap Modal JS
import { computed, onMounted, ref } from 'vue'
import apiService from '../services/apiService' // Import the API service

const historyRecords = ref([])
const templates = ref([]) // To map template IDs to names/types
const loadingHistory = ref(true)
const historyError = ref(null)
const filters = ref({ docType: '', status: '', date: '' }) // Status and date filters not fully implemented yet
const selectedRecordDetails = ref(null) // Details for the modal
const loadingDetails = ref(false)
const detailsError = ref(null)

// Computed property for unique document types in the history
const uniqueDocTypes = computed(() => {
  const types = historyRecords.value
    .map((record) => {
      const template = templates.value.find((tpl) => tpl.id === record.template_id)
      return template ? template.document_type : 'Unknown'
    })
    .filter((type) => type !== 'Unknown') // Optionally filter out 'Unknown'
  return [...new Set(types)] // Return unique types
})

// Filtered history records based on docType filter
const filteredHistory = computed(() => {
  return historyRecords.value.filter((record) => {
    const template = templates.value.find((tpl) => tpl.id === record.template_id)
    const recordDocType = template ? template.document_type : 'Unknown'
    return (
      !filters.value.docType || recordDocType === filters.value.docType
      // Add logic for status and date filters when backend supports
      // && (!filters.value.status || record.status === filters.value.status)
      // && (!filters.value.date || record.generated_at.startsWith(filters.value.date)) // Needs proper date comparison
    )
  })
})

// Fetch history and templates on component mount
onMounted(async () => {
  await fetchHistory()
  await fetchTemplates() // Fetch templates to map IDs
})

const fetchHistory = async () => {
  loadingHistory.value = true
  historyError.value = null
  try {
    historyRecords.value = await apiService.getHistory()
  } catch (error) {
    historyError.value = error.message
  } finally {
    loadingHistory.value = false
  }
}

const fetchTemplates = async () => {
  // Fetch templates silently as they are just for display mapping
  try {
    templates.value = await apiService.getTemplates()
  } catch (error) {
    console.error('Failed to fetch templates for history view:', error)
    // Don't block history display if templates fail to load
  }
}

const viewDetails = async (historyId) => {
  selectedRecordDetails.value = null // Clear previous details
  loadingDetails.value = true
  detailsError.value = null

  try {
    selectedRecordDetails.value = await apiService.getHistoryItem(historyId)
    // Show the modal
    const modalElement = document.getElementById('historyDetailModal')
    const modal = new Modal(modalElement)
    modal.show()
  } catch (error) {
    detailsError.value = error.message
  } finally {
    loadingDetails.value = false
  }
}

// Helper to get template name by ID
const getTemplateName = (templateId) => {
  const template = templates.value.find((tpl) => tpl.id === templateId)
  return template ? template.name : null
}

// Helper to get template document type by ID
const getTemplateDocType = (templateId) => {
  const template = templates.value.find((tpl) => tpl.id === templateId)
  return template ? template.document_type : null
}

// Helper to format date string
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }
    return new Date(dateString).toLocaleDateString(undefined, options)
  } catch (e) {
    console.error('Error formatting date:', dateString, e)
    return dateString // Return original if formatting fails
  }
}

// Helper to format input data (parse JSON string)
const formatInputData = (inputDataString) => {
  if (!inputDataString) return '{}'
  try {
    const data = JSON.parse(inputDataString)
    return JSON.stringify(data, null, 2) // Pretty print JSON
  } catch (e) {
    console.error('Error parsing input data JSON:', inputDataString, e)
    return inputDataString // Return original string if parsing fails
  }
}

// Mock download - this will need to be updated later
const download = (record) => {
  alert(`Downloading ${record.id}`)
  // TODO: Implement actual download logic when backend supports
}

const resetFilters = () => {
  filters.value = { docType: '', status: '', date: '' }
}

// Status badge class (mock status for now)
// const badgeClass = (s) => {
//   return s === 'Success' ? 'bg-success-subtle' : s === 'Failed' ? 'bg-danger-subtle' : 'bg-warning-subtle';
// };
</script>

<style scoped>
.alert-pre {
  white-space: pre-wrap; /* Preserve whitespace and wrap long lines */
  word-wrap: break-word;
}
</style>
