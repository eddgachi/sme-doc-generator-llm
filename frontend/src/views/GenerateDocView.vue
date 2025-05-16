<template>
  <div class="container-fluid p-4">
    <h2 class="mb-4">Generate Document</h2>
    <p class="text-muted mb-4">Select a document type and fill in the details to generate a document.</p>

    <div class="card mb-4">
      <div class="card-header">Select Document Template</div>
      <div class="card-body">
        <div v-if="loadingTemplates" class="text-center p-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading Templates...</span>
          </div>
          <p class="mt-2">Loading available document types...</p>
        </div>
        <div v-else>
          <div class="mb-3">
            <label for="docType" class="form-label">Document Template</label>
            <select id="docType" class="form-select" v-model="selectedTemplateId" @change="onTemplateSelect">
              <option value="">-- Select Document Template --</option>
              <option v-for="tpl in activeTemplates" :key="tpl.id" :value="tpl.id">
                {{ tpl.name }} ({{ tpl.document_type }})
              </option>
            </select>
          </div>

          <div v-if="selectedTemplate">
            <h3 class="h6 mt-4 mb-3">Details for {{ selectedTemplate.name }} ({{ selectedTemplate.document_type }})</h3>
            <div class="alert alert-info small">Fill out the fields below to generate your document.</div>

            <div class="mb-3" v-for="(placeholder, idx) in templatePlaceholders" :key="idx">
              <label :for="'input-' + placeholder" class="form-label">{{ formatPlaceholderLabel(placeholder) }}</label>
              <input
                :id="'input-' + placeholder"
                v-model="formData[placeholder]"
                type="text"
                class="form-control"
                :placeholder="'Enter ' + formatPlaceholderLabel(placeholder).toLowerCase()"
              />
            </div>

            <div class="mb-3">
              <label for="outputFormat" class="form-label">Output Format</label>
              <select id="outputFormat" class="form-select" v-model="outputFormat">
                <option value="pdf">PDF</option>
                <option value="docx">DOCX</option>
              </select>
            </div>

            <button class="btn btn-primary mt-3" @click="generateDocument" :disabled="loading || !isFormDataComplete">
              {{ loading ? 'Generating...' : 'Generate Document' }}
            </button>
          </div>
          <div v-else-if="!loadingTemplates && activeTemplates.length === 0" class="alert alert-warning mt-3">
            No active document templates found. Please go to Template Management to create or activate templates.
          </div>
        </div>
      </div>
    </div>

    <div class="card" v-if="generatedDoc">
      <div class="card-header">Document Preview</div>
      <div class="card-body">
        <div class="alert alert-success small">Content generated successfully.</div>
        <div class="border p-3 rounded bg-light-subtle" style="min-height: 200px">
          <pre class="mb-0">{{ generatedDoc.generated_content }}</pre>
        </div>
        <button class="btn btn-success mt-3" @click="downloadDocument">
          Download Document ({{ generatedDoc.document_format.toUpperCase() }})
        </button>
        <small v-if="generatedDoc.history_id" class="form-text text-muted ms-2"
          >History ID: {{ generatedDoc.history_id }}</small
        >
      </div>
    </div>

    <div v-if="message" :class="['mt-4 alert', message.type === 'success' ? 'alert-success' : 'alert-danger']">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup>
import { saveAs } from 'file-saver' // You'll need to install file-saver: npm install file-saver
import { computed, onMounted, ref, watch } from 'vue'
import apiService from '../services/apiService' // Import the API service

const templates = ref([]) // All templates from the backend
const loadingTemplates = ref(true)
const selectedTemplateId = ref('')
const selectedTemplate = ref(null) // The currently selected template object
const formData = ref({}) // Data for the dynamic form
const loading = ref(false) // Loading state for generation
const generatedDoc = ref(null) // Stores the response from the generate endpoint
const outputFormat = ref('pdf') // Default output format
const message = ref(null) // For success/error messages

// Filter for active templates
const activeTemplates = computed(() => templates.value.filter((tpl) => tpl.is_active))

// Extract placeholders from the selected template content
const templatePlaceholders = computed(() => {
  if (!selectedTemplate.value || !selectedTemplate.value.template_content) return []
  const regex = /{([^}]+)}/g
  const matches = selectedTemplate.value.template_content.match(regex)
  if (!matches) return []
  // Remove curly braces and return unique placeholders
  return [...new Set(matches.map((match) => match.slice(1, -1)))]
})

// Check if all required form data is complete
const isFormDataComplete = computed(() => {
  // Check if there's a selected template and if all placeholders have corresponding data in formData
  if (!selectedTemplate.value) return false
  return templatePlaceholders.value.every(
    (placeholder) => formData.value[placeholder] !== undefined && formData.value[placeholder] !== ''
  )
})

// Fetch templates on component mount
onMounted(async () => {
  await fetchTemplates()
})

// Watch for selectedTemplateId changes to update the form
watch(selectedTemplateId, (newId) => {
  selectedTemplate.value = templates.value.find((tpl) => tpl.id === newId) || null
  // Reset formData when template changes
  formData.value = {}
  generatedDoc.value = null // Clear previous preview
  message.value = null // Clear messages
})

const fetchTemplates = async () => {
  loadingTemplates.value = true
  try {
    templates.value = await apiService.getTemplates()
  } catch (error) {
    message.value = { type: 'danger', text: `Failed to load templates: ${error.message}` }
  } finally {
    loadingTemplates.value = false
  }
}

const onTemplateSelect = () => {
  // Logic handled by the watch effect on selectedTemplateId
}

const generateDocument = async () => {
  if (!selectedTemplate.value || !isFormDataComplete.value) {
    message.value = { type: 'danger', text: 'Please select a template and fill all required fields.' }
    return
  }

  loading.value = true
  generatedDoc.value = null
  message.value = null

  try {
    // Prepare the request payload
    const generationRequestData = {
      template_id: selectedTemplate.value.id,
      input_data: JSON.stringify(formData.value), // Send formData as a JSON string
      document_format: outputFormat.value, // Send the selected format
    }

    const result = await apiService.generateDocument(generationRequestData)

    generatedDoc.value = result // Store the generated content and history ID
    message.value = { type: 'success', text: 'Document generated successfully!' }

    // TODO: Implement actual PDF/DOCX download using the generated content
    // The backend currently returns text. You would need a backend endpoint
    // that takes the generated_content (and format) and returns a file.
    // For now, the download button will save the raw text.
  } catch (error) {
    message.value = { type: 'danger', text: `Document generation failed: ${error.message}` }
  } finally {
    loading.value = false
  }
}

const downloadDocument = () => {
  if (!generatedDoc.value || !generatedDoc.value.generated_content) {
    message.value = { type: 'danger', text: 'No document content to download.' }
    return
  }

  // For now, save the raw text content.
  // When backend supports file generation, this function will need to be updated
  // to call a backend download endpoint or handle the file blob.
  const blob = new Blob([generatedDoc.value.generated_content], { type: 'text/plain' })
  const filename = `${selectedTemplate.value.name || 'document'}.${generatedDoc.value.document_format || 'txt'}`
  saveAs(blob, filename)

  message.value = { type: 'success', text: `Downloading document as ${filename}.` }
}

// Helper to format placeholder keys into more readable labels
const formatPlaceholderLabel = (key) => {
  // Replace underscores with spaces and capitalize first letter of each word
  return key.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}
</script>

<style scoped>
/* scoped styles if needed */
</style>
