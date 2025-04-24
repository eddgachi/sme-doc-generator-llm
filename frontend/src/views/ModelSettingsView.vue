// ModelSettingsView.vue
<template>
  <div class="container-fluid p-4">
    <h2 class="mb-4">LLM Settings</h2>
    <p class="text-muted mb-4">Configure LLM parameters.</p>

    <div class="card">
      <div class="card-body">
        <div class="mb-3">
          <label for="modelName" class="form-label">Model Name</label>
          <input id="modelName" class="form-control" v-model="settings.modelName" placeholder="gpt-3.5-turbo" />
        </div>
        <div class="mb-3">
          <label for="temperature" class="form-label">Temperature</label>
          <input
            id="temperature"
            type="number"
            step="0.1"
            min="0"
            max="2"
            class="form-control"
            v-model.number="settings.temperature"
          />
        </div>
        <div class="mb-3">
          <label for="maxTokens" class="form-label">Max Tokens</label>
          <input id="maxTokens" type="number" min="50" class="form-control" v-model.number="settings.maxTokens" />
        </div>
        <button class="btn btn-primary me-2" @click="saveSettings">Save</button>
        <button class="btn btn-outline-secondary" @click="testConnection">Test</button>
      </div>
    </div>

    <div v-if="testResult" :class="['mt-4 alert', testResult.success ? 'alert-success' : 'alert-danger']">
      <strong>{{ testResult.success ? 'Success' : 'Error' }}</strong>
      <p>{{ testResult.message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const settings = ref({ modelName: 'gpt-3.5-turbo', temperature: 0.7, maxTokens: 1024 })
const testResult = ref(null)

function saveSettings() {
  alert(`Saved: ${JSON.stringify(settings.value)}`)
}

function testConnection() {
  testResult.value = null
  setTimeout(() => {
    const success = Math.random() > 0.2
    testResult.value = { success, message: success ? 'Connected to LLM (mock).' : 'Connection failed (mock).' }
  }, 1000)
}
</script>

<style scoped></style>
