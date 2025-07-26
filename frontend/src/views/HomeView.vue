<!-- The parent component managing state and components -->
<script setup>
import { ref, onMounted } from 'vue'
import TransactionForm from '@/components/TransactionForm.vue'
import TransactionList from '@/components/TransactionList.vue'

// The main reactive array that will hold the transaction data
const transactions = ref([])

// Function to fetch data from BE
const fetchTransactions = async () => {
  try {
    const response = await fetch('http://localhost:8000/transactions/')
    if (!response.ok) {
      throw new Error('Failed to fetch transactions.')
    }
    const data = await response.json()
    transactions.value = data  // Update reactive array with fetched data
  } catch (error) {
    console.error('Error fetching transactions:', error)
  }
}

// onMounted is a lifecycle hook that runs once when the component is created.
// Call fecth here to load initial data
onMounted(() => {
  fetchTransactions()
})
</script>

<template>
  <main>
    <div class="container">
      <TransactionForm @transaction-added="fetchTransactions" />
      <TransactionList :transactions="transactions" />
    </div>
  </main>
</template>

<style scoped>
.container {
  max-width: 960px;
  margin: 2rem auto;
  padding: 0 1rem;
}
</style>