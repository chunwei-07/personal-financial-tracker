<script setup>
import { ref, onMounted } from 'vue'

// Create a reactive reference to hold our message
const message = ref('Connecting to backend...')

// This function will run automatically when the component is first loaded
onMounted(async () => {
  try {
    // Use the browser's fetch API to make a request to our backend
    const response = await fetch('http://localhost:8000/')
    const data = await response.json()

    // Update the message with the data we received
    message.value = data.message
  } catch (error) {
    // If an error occurs, display it
    message.value = 'Failed to connect to backend. Is it running?'
    console.error(error)
  }
})
</script>

<template>
  <main>
    <h1>{{ message }}</h1>
  </main>
</template>

<style scoped>
main {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80vh;
  font-family: sans-serif;
}
h1 {
  font-size: 2rem;
  color: #333;
}
</style>
