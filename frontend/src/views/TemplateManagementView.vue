<template>
  <div class="container-fluid p-4">
    <h2 class="mb-4">Template Management</h2>
    <p class="text-muted mb-4">Manage prompt templates for document generation.</p>

    <div class="card mb-4">
      <div class="card-header">Create New Template</div>
      <div class="card-body">
        <div v-if="creatingTemplate" class="text-center p-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Creating...</span>
          </div>
          <p class="mt-2">Creating template...</p>
        </div>
        <div v-else>
          <div class="mb-3">
            <label for="newName" class="form-label">Template Name</label>
            <input id="newName" class="form-control" v-model="newTemplate.name" placeholder="e.g., Standard Invoice" />
          </div>
          <div class="mb-3">
            <label for="newDocType" class="form-label">Document Type</label>
            <select id="newDocType" class="form-select" v-model="newTemplate.document_type">
              <option value="">-- Select Type --</option>
              <option v-for="type in availableDocTypes" :key="type" :value="type">{{ type }}</option>
            </select>
          </div>
          <div class="mb-3">
            <label for="newTemplateContent" class="form-label">Template Content (with {placeholders})</label>
            <textarea
              id="newTemplateContent"
              rows="6"
              class="form-control"
              v-model="newTemplate.template_content"
              placeholder="e.g., Subject: Invoice {invoice_number}\n\nDear {client_name},..."
            />
          </div>
          <div class="form-check mb-3">
            <input id="newIsActive" class="form-check-input" type="checkbox" v-model="newTemplate.is_active" />
            <label class="form-check-label" for="newIsActive">Active</label>
          </div>
          <button class="btn btn-primary" @click="createTemplate">Create Template</button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">Existing Templates</div>
      <div v-if="loadingTemplates" class="text-center p-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Loading templates...</p>
      </div>
      <div v-else class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tpl in templates" :key="tpl.id">
              <td>{{ tpl.name }}</td>
              <td>{{ tpl.document_type }}</td>
              <td>
                <span
                  :class="[
                    'badge',
                    tpl.is_active ? 'bg-success-subtle text-success-emphasis' : 'bg-danger-subtle text-danger-emphasis',
                  ]"
                >
                  {{ tpl.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-2" @click="editTemplate(tpl)">Edit</button>
                <button class="btn btn-sm btn-outline-secondary me-2" @click="startTestPrompt(tpl)">Test</button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteTemplate(tpl.id)">Delete</button>
              </td>
            </tr>
            <tr v-if="templates.length === 0">
              <td colspan="4" class="text-center p-5 text-muted">No templates found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="editingTemplate" class="mt-4">
      <h3 class="h6 mb-3">Edit: {{ editingTemplate.name }}</h3>
      <div class="card">
        <div v-if="savingTemplate" class="text-center p-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Saving...</span>
          </div>
          <p class="mt-2">Saving template...</p>
        </div>
        <div v-else class="card-body">
          <div class="mb-3">
            <label for="editName" class="form-label">Template Name</label>
            <input id="editName" class="form-control" v-model="editingTemplate.name" />
          </div>
          <div class="mb-3">
            <label for="editDocType" class="form-label">Document Type</label>
            <select id="editDocType" class="form-select" v-model="editingTemplate.document_type" disabled>
              <option v-for="type in availableDocTypes" :key="type" :value="type">{{ type }}</option>
            </select>
            <small class="form-text text-muted">Document type cannot be changed after creation.</small>
          </div>
          <div class="mb-3">
            <label for="editTemplateContent" class="form-label">Template Content (with {placeholders})</label>
            <textarea
              id="editTemplateContent"
              rows="6"
              class="form-control"
              v-model="editingTemplate.template_content"
            />
          </div>
          <div class="form-check mb-3">
            <input id="editIsActive" class="form-check-input" type="checkbox" v-model="editingTemplate.is_active" />
            <label class="form-check-label" for="editIsActive">Active</label>
          </div>
          <button class="btn btn-primary me-2" @click="saveTemplate">Save Changes</button>
          <button class="btn btn-secondary" @click="cancelEdit">Cancel</button>
        </div>
      </div>
    </div>

    <div v-if="testingTemplate" class="mt-4">
      <h3 class="h6 mb-3">Test: {{ testingTemplate.name }}</h3>
      <div class="card">
        <div v-if="testingPrompt" class="text-center p-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Testing...</span>
          </div>
          <p class="mt-2">Sending test prompt...</p>
        </div>
        <div v-else class="card-body">
          <div class="alert alert-info small">
            Enter sample data for the placeholders in the template content.
            <br />
            <strong>Placeholders in template:</strong>
            {{ extractPlaceholders(testingTemplate.template_content).join(', ') || 'None' }}
          </div>
          <div class="mb-3">
            <label for="testInputData" class="form-label">Test Input Data (JSON)</label>
            <textarea
              id="testInputData"
              rows="6"
              class="form-control font-monospace small"
              v-model="testInputDataJson"
              placeholder='e.g., {"client_name": "Acme Corp", "amount": 1000}'
            />
          </div>
          <button class="btn btn-primary me-2" @click="testPrompt">Run Test</button>
          <button class="btn btn-secondary" @click="cancelTest">Cancel</button>

          <div v-if="testResult" :class="['mt-4 alert', testResult.success ? 'alert-success' : 'alert-danger']">
            <strong>Test Result:</strong>
            <pre class="alert-pre mb-0">{{ testResult.output }}</pre>
          </div>
          <div v-if="testError" class="mt-4 alert alert-danger"><strong>Test Error:</strong> {{ testError }}</div>
        </div>
      </div>
    </div>

    <div v-if="message" :class="['mt-4 alert', message.type === 'success' ? 'alert-success' : 'alert-danger']">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import apiService from '../services/apiService' // Import the API service

const templates = ref([])
const loadingTemplates = ref(true)
const editingTemplate = ref(null)
const savingTemplate = ref(false)
const testingTemplate = ref(null) // Template currently being tested
const testInputDataJson = ref('{}') // JSON string for test input data
const testingPrompt = ref(false)
const testResult = ref(null)
const testError = ref(null)
const message = ref(null) // For general success/error messages

// Data for creating a new template
const newTemplate = ref({
  name: '',
  document_type: '',
  template_content: '',
  is_active: true,
})
const creatingTemplate = ref(false)

// Available document types (can be fetched from backend if an endpoint exists, or hardcoded)
const availableDocTypes = ['Quote', 'Invoice', 'LPO', 'Contract']

// Fetch templates when the component is mounted
onMounted(async () => {
  await fetchTemplates()
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

const createTemplate = async () => {
  creatingTemplate.value = true
  message.value = null
  testResult.value = null
  testError.value = null
  try {
    const created = await apiService.createTemplate(newTemplate.value)
    message.value = { type: 'success', text: `Template '${created.name}' created successfully.` }
    // Clear the form
    newTemplate.value = { name: '', document_type: '', template_content: '', is_active: true }
    // Refresh the list
    await fetchTemplates()
  } catch (error) {
    message.value = { type: 'danger', text: `Failed to create template: ${error.message}` }
  } finally {
    creatingTemplate.value = false
  }
}

const editTemplate = (tpl) => {
  // Create a deep copy to avoid modifying the list directly before saving
  editingTemplate.value = JSON.parse(JSON.stringify(tpl))
  // Close testing section if open
  testingTemplate.value = null
  testResult.value = null
  testError.value = null
}

const saveTemplate = async () => {
  if (!editingTemplate.value) return

  savingTemplate.value = true
  message.value = null
  try {
    const updated = await apiService.updateTemplate(editingTemplate.value.id, editingTemplate.value)
    message.value = { type: 'success', text: `Template '${updated.name}' updated successfully.` }
    editingTemplate.value = null // Close edit section
    await fetchTemplates() // Refresh the list
  } catch (error) {
    message.value = { type: 'danger', text: `Failed to save template: ${error.message}` }
  } finally {
    savingTemplate.value = false
  }
}

const cancelEdit = () => {
  editingTemplate.value = null
}

const deleteTemplate = async (templateId) => {
  if (confirm('Are you sure you want to delete this template?')) {
    message.value = null
    try {
      await apiService.deleteTemplate(templateId)
      message.value = { type: 'success', text: 'Template deleted successfully.' }
      await fetchTemplates() // Refresh the list
      // Close edit/test sections if the deleted template was open
      if (editingTemplate.value && editingTemplate.value.id === templateId) editingTemplate.value = null
      if (testingTemplate.value && testingTemplate.value.id === templateId) testingTemplate.value = null
      testResult.value = null
      testError.value = null
    } catch (error) {
      message.value = { type: 'danger', text: `Failed to delete template: ${error.message}` }
    }
  }
}

const startTestPrompt = (tpl) => {
  // Create a copy for testing
  testingTemplate.value = JSON.parse(JSON.stringify(tpl))
  testInputDataJson.value = '{}' // Reset test input data
  testResult.value = null // Clear previous test results
  testError.value = null
  // Close edit section if open
  editingTemplate.value = null
}

const testPrompt = async () => {
  if (!testingTemplate.value) return

  testingPrompt.value = true
  testResult.value = null
  testError.value = null

  try {
    // Parse the JSON input data string
    const inputData = JSON.parse(testInputDataJson.value)

    const result = await apiService.testTemplate(testingTemplate.value.id, inputData)
    testResult.value = { success: true, output: result.test_output }
  } catch (error) {
    // Handle JSON parsing errors or API errors
    if (error instanceof SyntaxError) {
      testError.value = `Invalid JSON in test input data: ${error.message}`
    } else {
      testError.value = `Test failed: ${error.message}`
    }
    testResult.value = { success: false, output: null } // Ensure testResult reflects failure
  } finally {
    testingPrompt.value = false
  }
}

const cancelTest = () => {
  testingTemplate.value = null
  testResult.value = null
  testError.value = null
}

// Helper to extract placeholders from template content
const extractPlaceholders = (content) => {
  if (!content) return []
  const regex = /{([^}]+)}/g
  const matches = content.match(regex)
  if (!matches) return []
  // Remove curly braces and return unique placeholders
  return [...new Set(matches.map((match) => match.slice(1, -1)))]
}
</script>

<style scoped>
.alert-pre {
  white-space: pre-wrap; /* Preserve whitespace and wrap long lines */
  word-wrap: break-word;
}
</style>
