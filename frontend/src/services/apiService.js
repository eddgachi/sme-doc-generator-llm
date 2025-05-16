// frontend/src/services/apiService.js
import apiClient from '../api'

// Helper function to handle API errors
const handleApiError = (error) => {
  console.error('API call failed:', error.response || error.message)
  const message =
    error.response && error.response.data && error.response.data.detail
      ? error.response.data.detail
      : error.message || 'An unexpected error occurred.'

  // You might want to use a global notification system here instead of throwing
  // For now, we re-throw so components can catch and display
  throw new Error(message)
}

// --- LLM Settings Endpoints ---
const getLLMSettings = async () => {
  try {
    const response = await apiClient.get('/settings/llm')
    // The backend now returns a list of objects with config_key, config_value, description
    // Convert this list into a simple key-value object for easier use in the form
    const settingsObject = response.data.reduce((acc, setting) => {
      acc[setting.config_key] = setting.config_value
      return acc
    }, {})
    return settingsObject
  } catch (error) {
    handleApiError(error)
  }
}

const updateLLMSettings = async (settingsData) => {
  try {
    // Send the settings data as a flat object matching the LLMSettingsUpdate schema
    const response = await apiClient.put('/settings/llm', settingsData)
    return response.data // Returns a success message
  } catch (error) {
    handleApiError(error)
  }
}

const testLLMConnection = async () => {
  try {
    const response = await apiClient.get('/settings/llm/test-connection')
    return response.data // Returns { status, message, model, sample_reply }
  } catch (error) {
    handleApiError(error)
  }
}

// --- Prompt Template Endpoints ---
const getTemplates = async () => {
  try {
    const response = await apiClient.get('/templates')
    return response.data // Returns a list of template objects
  } catch (error) {
    handleApiError(error)
  }
}

const createTemplate = async (templateData) => {
  try {
    const response = await apiClient.post('/templates', templateData)
    return response.data // Returns the created template object
  } catch (error) {
    handleApiError(error)
  }
}

const updateTemplate = async (templateId, templateData) => {
  try {
    const response = await apiClient.put(`/templates/${templateId}`, templateData)
    return response.data // Returns the updated template object
  } catch (error) {
    handleApiError(error)
  }
}

const deleteTemplate = async (templateId) => {
  try {
    // FastAPI returns 204 No Content for successful deletion, no data in response
    await apiClient.delete(`/templates/${templateId}`)
    return true // Indicate success
  } catch (error) {
    handleApiError(error)
  }
}

const testTemplate = async (templateId, inputData) => {
  try {
    // The backend /test endpoint expects the raw inputData dictionary directly
    const response = await apiClient.post(`/templates/${templateId}/test`, inputData)
    return response.data // Returns { template_id, test_output }
  } catch (error) {
    handleApiError(error)
  }
}

// --- Document Generation Endpoint ---
const generateDocument = async (generationRequestData) => {
  try {
    // The backend /generate endpoint expects { template_id, input_data (JSON string), document_format }
    const response = await apiClient.post('/generate', generationRequestData)
    return response.data // Returns { history_id, generated_content, document_format }
  } catch (error) {
    handleApiError(error)
  }
}

// --- Document History Endpoints ---
const getHistory = async (skip = 0, limit = 100) => {
  try {
    const response = await apiClient.get('/history/docs', {
      params: { skip, limit },
    })
    return response.data // Returns a list of history objects
  } catch (error) {
    handleApiError(error)
  }
}

const getHistoryItem = async (historyId) => {
  try {
    const response = await apiClient.get(`/history/docs/${historyId}`)
    return response.data // Returns a single history object
  } catch (error) {
    handleApiError(error)
  }
}

// Export all service functions
export default {
  getLLMSettings,
  updateLLMSettings,
  testLLMConnection,
  getTemplates,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  testTemplate,
  generateDocument,
  getHistory,
  getHistoryItem,
}
