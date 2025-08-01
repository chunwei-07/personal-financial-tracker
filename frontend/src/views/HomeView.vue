<!-- The parent component managing state and components -->
<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import TransactionForm from '@/components/TransactionForm.vue'
import TransactionList from '@/components/TransactionList.vue'
import ExpenseChart from '@/components/ExpenseChart.vue'
import EditTransactionModal from '@/components/EditTransactionModal.vue'

// The main reactive array that will hold the transaction data
const transactions = ref([])
const expenseSummary = ref([])
const isEditModalVisible = ref(false)
const transactionToEdit = ref(null)

// Function to fetch summary data from new endpoint
const fetchExpenseSummary = async () => {
  try {
    const response = await fetch('/transactions/summary/monthly-expenses')
    if (!response.ok) throw new Error('Failed to fetch summary')
    expenseSummary.value = await response.json()
  } catch (error) {
    console.error('Error fetching summary:', error)
  }
}

// Function to fetch data from BE
const fetchTransactions = async () => {
  try {
    const response = await fetch('/transactions/')
    if (!response.ok) {
      throw new Error('Failed to fetch transactions.')
    }
    const data = await response.json()
    transactions.value = data  // Update reactive array with fetched data
  } catch (error) {
    console.error('Error fetching transactions:', error)
  }
}

// Function to open Edit modal
const openEditModal = (transaction) => {
  transactionToEdit.value = transaction
  isEditModalVisible.value = true
}

// Function that runs whenever a transaction is added
const handleTransactionAdded = () => {
  fetchTransactions()
  fetchExpenseSummary()
}

// onMounted is a lifecycle hook that runs once when the component is created.
// Call fecth here to load initial data
onMounted(() => {
  fetchTransactions()
  fetchExpenseSummary()
})

const chartData = computed(() => {
  const labels = Object.keys(expenseSummary.value)
  const data = Object.values(expenseSummary.value)

  return {
    labels: labels,
    datasets: [
      {
        backgroundColor: ['#41B883', '#E46651', '#00D8FF', '#DD1B16', '#F4D03F', '#5D6D7E'],
        data: data
      }
    ]
  }
})
</script>

<template>
  <main>
    <div class="container">
      <ExpenseChart v-if="Object.keys(expenseSummary).length > 0" :chart-data="chartData" />
      <TransactionForm @transaction-added="handleTransactionAdded" />
      <TransactionList
        :transactions="transactions" 
        @transaction-deleted="handleTransactionAdded"
        @edit="openEditModal"
      />
    </div>

    <EditTransactionModal
      :show="isEditModalVisible"
      :transaction="transactionToEdit"
      @close="isEditModalVisible = false"
      @transaction-updated="handleTransactionAdded"
    />
  </main>
</template>

<style scoped>
.container {
  max-width: 960px;
  margin: 2rem auto;
  padding: 0 1rem;
}
</style>