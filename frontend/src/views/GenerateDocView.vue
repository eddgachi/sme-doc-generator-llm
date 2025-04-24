// GenerateDocView.vue
<template>
  <div class="container-fluid p-4">
    <h2 class="mb-4">Generate Document</h2>
    <p class="text-muted mb-4">Select a document type and fill in the details to generate a document.</p>

    <div class="card mb-4">
      <div class="card-header">Select Document Type</div>
      <div class="card-body">
        <div class="mb-3">
          <label for="docType" class="form-label">Document Type</label>
          <select id="docType" class="form-select" v-model="selectedDocType">
            <option value="">-- Select --</option>
            <option v-for="type in docTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </div>

        <div v-if="selectedDocType">
          <h3 class="h6 mt-4 mb-3">Details for {{ selectedDocType }}</h3>
          <div class="alert alert-info small">Fill out the fields below to generate your {{ selectedDocType }}.</div>
          <div class="mb-3" v-for="(field, idx) in dynamicFields" :key="idx">
            <label :for="field.key" class="form-label">{{ field.label }}</label>
            <component
              :is="field.type === 'textarea' ? 'textarea' : 'input'"
              :id="field.key"
              v-model="formData[field.key]"
              :rows="field.type === 'textarea' ? 3 : null"
              class="form-control"
              :placeholder="field.placeholder"
            />
          </div>
          <button class="btn btn-primary mt-3" @click="generateDocument" :disabled="loading">
            {{ loading ? 'Generating...' : 'Generate Document' }}
          </button>
        </div>
      </div>
    </div>

    <div class="card" v-if="generatedDocPreview">
      <div class="card-header">Document Preview</div>
      <div class="card-body">
        <div class="alert alert-success small">Live preview below.</div>
        <div class="border p-3 rounded bg-light-subtle" style="min-height: 200px">
          <pre class="mb-0">{{ generatedDocPreview.content }}</pre>
        </div>
        <button class="btn btn-success mt-3" @click="downloadDocument">Download Document</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const docTypes = ['Quote', 'Invoice', 'LPO', 'Contract']
const selectedDocType = ref('')
const loading = ref(false)
const generatedDocPreview = ref(null)

// Mock dynamic fields per doc type
const fieldsMap = {
  Quote: [
    { key: 'clientName', label: 'Client Name', type: 'text', placeholder: 'Enter client name' },
    { key: 'amount', label: 'Amount', type: 'text', placeholder: 'Enter amount' },
  ],
  Invoice: [
    { key: 'invoiceNumber', label: 'Invoice Number', type: 'text', placeholder: 'INV-123' },
    { key: 'dueDate', label: 'Due Date', type: 'text', placeholder: 'YYYY-MM-DD' },
  ],
  LPO: [
    { key: 'poNumber', label: 'PO Number', type: 'text', placeholder: 'PO-456' },
    { key: 'supplier', label: 'Supplier', type: 'text', placeholder: 'Enter supplier name' },
  ],
  Contract: [
    { key: 'partyA', label: 'Party A', type: 'text', placeholder: 'Enter first party' },
    { key: 'partyB', label: 'Party B', type: 'text', placeholder: 'Enter second party' },
  ],
}

const dynamicFields = computed(() => fieldsMap[selectedDocType.value] || [])
const formData = ref({})

function generateDocument() {
  loading.value = true
  // Simulate API call
  setTimeout(() => {
    generatedDocPreview.value = {
      content: `Generated ${selectedDocType.value}:\n` + JSON.stringify(formData.value, null, 2),
    }
    loading.value = false
  }, 1000)
}

function downloadDocument() {
  // Mock download
  const blob = new Blob([generatedDocPreview.value.content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${selectedDocType.value}.${'txt'}`
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
/* scoped styles if needed */
</style>
