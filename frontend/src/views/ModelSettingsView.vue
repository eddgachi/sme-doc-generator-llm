<template>
  <div class="container-fluid p-4">
    <h2 class="mb-4">LLM Settings</h2>
    <p class="text-muted mb-4">Configure LLM parameters.</p>

    <div class="card">
      <div class="card-body">
        <div v-if="loadingSettings" class="text-center p-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading Settings...</span>
          </div>
          <p class="mt-2">Loading settings...</p>
        </div>

        <div v-else>
          <div class="mb-3" v-for="(setting, key) in settings" :key="key">
            <label :for="key" class="form-label">{{ setting.description || key }}</label>
            <input
              v-if="key !== 'google_api_key' && key !== 'cors_allowed_origins' && key !== 'llm_system_message'"
              :id="key"
              :type="getInputType(key)"
              :step="key === 'llm_temperature' ? '0.1' : null"
              :min="key === 'llm_temperature' ? '0' : key === 'llm_max_tokens' ? '50' : null"
              :max="key === 'llm_temperature' ? '1' : null"
              class="form-control"
              v-model="settings[key].config_value"
              :placeholder="key"
            />
            <input
              v-else-if="key === 'google_api_key'"
              :id="key"
              type="password"
              class="form-control"
              v-model="settings[key].config_value"
              placeholder="Enter your Google AI API Key"
            />
            <textarea
              v-else-if="key === 'llm_system_message'"
              :id="key"
              rows="3"
              class="form-control"
              v-model="settings[key].config_value"
              :placeholder="key"
            ></textarea>
            <input
              v-else-if="key === 'cors_allowed_origins'"
              :id="key"
              type="text"
              class="form-control"
              v-model="settings[key].config_value"
              placeholder="Comma-separated origins"
            />
            <div v-else-if="key === 'enable_history'" class="form-check form-switch">
              <input
                class="form-check-input"
                type="checkbox"
                role="switch"
                :id="key"
                v-model="settings[key].config_value"
                :true-value="'true'"
                :false-value="'false'"
              />
              <label class="form-check-label" :for="key">{{ setting.description || key }}</label>
            </div>
          </div>

          <button class="btn btn-primary me-2" @click="saveSettings" :disabled="savingSettings">
            {{ savingSettings ? 'Saving...' : 'Save Settings' }}
          </button>
          <button class="btn btn-outline-secondary" @click="testConnection" :disabled="testingConnection">
            {{ testingConnection ? 'Testing...' : 'Test Connection' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="testResult" :class="['mt-4 alert', testResult.status === 'ok' ? 'alert-success' : 'alert-danger']">
      <strong>{{ testResult.status === 'ok' ? 'Success' : 'Error' }}</strong>
      <p>{{ testResult.message }}</p>
      <p v-if="testResult.sample_reply">Sample Reply: {{ testResult.sample_reply }}</p>
    </div>

    <div v-if="saveMessage" :class="['mt-4 alert', saveMessage.type === 'success' ? 'alert-success' : 'alert-danger']">
      {{ saveMessage.text }}
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import apiService from '../services/apiService' // Import the API service

const settings = ref({}) // Will store settings as key -> { config_key, config_value, description }
const testResult = ref(null)
const loadingSettings = ref(true)
const savingSettings = ref(false)
const testingConnection = ref(false)
const saveMessage = ref(null)

// Helper to determine input type based on key (basic guess)
const getInputType = (key) => {
  if (
    key.includes('temperature') ||
    key.includes('tokens') ||
    key.includes('count') ||
    key.includes('days') ||
    key.includes('seconds')
  ) {
    return 'number'
  }
  // Add more checks for date, email, etc. if needed for other settings
  return 'text'
}

// Fetch settings when the component is mounted
onMounted(async () => {
  await fetchSettings()
})

const fetchSettings = async () => {
  loadingSettings.value = true
  try {
    const fetchedSettings = await apiService.getLLMSettings()
    // Backend returns a list, convert to object keyed by config_key for easier form binding
    settings.value = fetchedSettings // apiService already converts to object
  } catch (error) {
    console.error('Failed to fetch settings:', error)
    // Optionally display an error message to the user
  } finally {
    loadingSettings.value = false
  }
}

const saveSettings = async () => {
  savingSettings.value = true
  saveMessage.value = null
  try {
    // Prepare data to send - send only the config_key and config_value
    const settingsToSave = Object.keys(settings.value).reduce((acc, key) => {
      // Only include keys that exist in the settings object
      if (settings.value[key] && settings.value[key].config_value !== undefined) {
        // For boolean settings, ensure they are sent as strings 'true' or 'false'
        if (key === 'enable_history') {
          acc[key] = String(settings.value[key].config_value)
        } else {
          acc[key] = settings.value[key].config_value
        }
      }
      return acc
    }, {})

    const response = await apiService.updateLLMSettings(settingsToSave)
    saveMessage.value = { type: 'success', text: response.message }
    // Re-fetch settings to get the masked API key back
    await fetchSettings()
  } catch (error) {
    saveMessage.value = { type: 'danger', text: error.message }
  } finally {
    savingSettings.value = false
  }
}

const testConnection = async () => {
  testingConnection.value = true
  testResult.value = null
  try {
    const result = await apiService.testLLMConnection()
    testResult.value = result
  } catch (error) {
    testResult.value = { status: 'error', message: error.message }
  } finally {
    testingConnection.value = false
  }
}
</script>

<style scoped>
/* scoped styles if needed */
</style>
