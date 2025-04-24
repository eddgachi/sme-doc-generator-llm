// ApiDocsView.vue
<template>
  <div class="container-fluid p-4">
    <h2 class="mb-4">API Documentation</h2>
    <p class="text-muted mb-4">Interactive Swagger UI from your FastAPI backend.</p>
    <div class="card">
      <iframe src="http://127.0.0.1:8000/docs#/" width="100%" height="800" loading="lazy"></iframe>
    </div>
  </div>
</template>

<script setup>
// This view embeds the live FastAPI Swagger UI served at http://127.0.0.1:8000/docs#/
// No additional logic required.
</script>

<style scoped>
iframe {
  border: none;
}
</style>
