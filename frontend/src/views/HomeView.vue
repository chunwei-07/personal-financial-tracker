<!-- The parent component managing state and components -->
<script setup>
import { ref, watch, onMounted } from 'vue'
import TransactionForm from '@/components/TransactionForm.vue'
import TransactionList from '@/components/TransactionList.vue'
import EditTransactionModal from '@/components/EditTransactionModal.vue'
import PaginationControls from '@/components/PaginationControls.vue'

// --- STATE MANAGEMENT ---
const transactions = ref([])
const isEditModalVisible = ref(false)
const transactionToEdit = ref(null)

// --- New Pagination State ---
const currentPage = ref(1);
const itemsPerPage = ref(10);
const totalTransactions = ref(0);

// API Function to fetch data from BE
const fetchTransactions = async () => {
  // Calculate skip value based on current page
  const skip = (currentPage.value - 1) * itemsPerPage.value;

  try {
    const response = await fetch(`/transactions/?skip=${skip}&limit=${itemsPerPage.value}`);
    if (!response.ok) throw new Error('Failed to fetch transactions');
    
    const data = await response.json();
    transactions.value = data.transactions;
    totalTransactions.value = data.total_count;

  } catch (error) {
    console.error('Error fetching transactions:', error)
  }
}

// Function that runs whenever a transaction is added
const handleTransactionAdded = () => {
  // When a transaction is added/edited/deleted, back to page 1
  if (currentPage.value !== 1) {
    currentPage.value = 1;
  } else {
    // If already on page 1, refresh data
    fetchTransactions();
  }
};

// Function to open Edit modal
const openEditModal = (transaction) => {
  transactionToEdit.value = transaction
  isEditModalVisible.value = true
};

// Page Change Handler
const handlePageChange = (newPage) => {
  currentPage.value = newPage;
};

// Watcher for changes
watch(currentPage, fetchTransactions);

// Lifecycle hook
onMounted(fetchTransactions);
</script>

<template>
  <main>
    <div class="container">
      <TransactionForm @transaction-added="handleTransactionAdded" />
      <TransactionList
        title="Recent Transactions"
        :transactions="transactions" 
        @transaction-deleted="handleTransactionAdded"
        @edit="openEditModal"
      />
      <PaginationControls
        :current-page="currentPage"
        :total-items="totalTransactions"
        :items-per-page="itemsPerPage"
        @page-changed="handlePageChange"
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