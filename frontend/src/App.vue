<script setup>
import { ref } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
const name = ref('world')
const result = ref('')
const loading = ref(false)

async function callApi(path) {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE_URL}${path}?name=${encodeURIComponent(name.value)}`)
    result.value = `${res.status} ${JSON.stringify(await res.json(), null, 2)}`
  } catch (err) {
    result.value = `Lỗi: ${err.message}`
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main>
    <h1>cicd-lab</h1>
    <input v-model="name" placeholder="name" />
    <button :disabled="loading" @click="callApi('hello')">GET /api/hello</button>
    <button :disabled="loading" @click="callApi('native/hello')">GET /api/native/hello</button>
    <button :disabled="loading" @click="callApi('health_check')">GET /api/health_check</button>
    <pre>{{ result }}</pre>
  </main>
</template>

<style>
main { font-family: sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; }
input, button { margin: 4px; padding: 6px 10px; }
pre { background: #f4f4f4; padding: 12px; white-space: pre-wrap; }
</style>
