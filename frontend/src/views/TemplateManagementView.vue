// TemplateManagementView.vue
<template>
  <div class="container-fluid p-4">
    <h2 class="mb-4">Template Management</h2>
    <p class="text-muted mb-4">Manage prompt templates for document generation.</p>

    <div class="card">
      <div class="card-body p-0">
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
              <td>{{ tpl.docType }}</td>
              <td>
                <span :class="['badge', tpl.isActive ? 'bg-success-subtle' : 'bg-danger-subtle']">
                  {{ tpl.isActive ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-2" @click="editTemplate(tpl)">Edit</button>
                <button class="btn btn-sm btn-outline-secondary" @click="testPrompt(tpl)">Test</button>
              </td>
            </tr>
            <tr v-if="templates.length === 0">
              <td colspan="4" class="text-center p-5 text-muted">No templates.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="editingTemplate" class="mt-4">
      <h3 class="h6 mb-3">Edit: {{ editingTemplate.name }}</h3>
      <div class="card">
        <div class="card-body">
          <div class="mb-3">
            <label for="promptText" class="form-label">Prompt Text</label>
            <textarea id="promptText" rows="6" class="form-control" v-model="editingTemplate.prompt" />
          </div>
          <div class="mb-3">
            <label for="placeholders" class="form-label">Placeholders (JSON)</label>
            <textarea id="placeholders" rows="3" class="form-control" v-model="editingTemplate.placeholders" />
          </div>
          <div class="form-check mb-3">
            <input id="isActive" class="form-check-input" type="checkbox" v-model="editingTemplate.isActive" />
            <label class="form-check-label" for="isActive">Active</label>
          </div>
          <button class="btn btn-primary me-2" @click="saveTemplate">Save</button>
          <button class="btn btn-secondary" @click="cancelEdit">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const templates = ref([
  { id: 1, name: 'Quote Basic', docType: 'Quote', prompt: 'Generate a quote...', placeholders: '{}', isActive: true },
  {
    id: 2,
    name: 'Invoice Std',
    docType: 'Invoice',
    prompt: 'Create an invoice...',
    placeholders: '{}',
    isActive: true,
  },
  { id: 3, name: 'LPO V1', docType: 'LPO', prompt: 'Draft an LPO...', placeholders: '{}', isActive: false },
])
const editingTemplate = ref(null)

function editTemplate(tpl) {
  editingTemplate.value = { ...tpl }
}

function saveTemplate() {
  const idx = templates.value.findIndex((t) => t.id === editingTemplate.value.id)
  if (idx !== -1) templates.value[idx] = { ...editingTemplate.value }
  editingTemplate.value = null
  alert('Template saved (mock).')
}

function cancelEdit() {
  editingTemplate.value = null
}

function testPrompt(tpl) {
  alert(`Mock test: ${tpl.prompt}`)
}
</script>

<style scoped></style>
