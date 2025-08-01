<!-- This component is to receive transactions list and display it nicely in a table -->
<script setup>
import { formatCurrency } from '@/utils/formatters'

// defineProps allows to declare data this component expects from parent
defineProps({
    transactions: {
        type: Array,
        required: true
    }
})

// --- HELPER FUNCTIONS ---
// UTC String to local time
const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString + 'Z')  // The 'Z' tells JS it's a UTC time
    return date.toLocaleString()   // Convert to local time
}

// Format currency
// const formatCurrency = (amount) => {
//     return new Intl.NumberFormat('en-US', {
//         style: 'currency',
//         currency: 'MYR'
//     }).format(amount)
// }

// Delete transaction
const emit = defineEmits(['transaction-deleted', 'edit'])

const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this transaction?')) {
        return
    }
    try {
        const response = await fetch(`/transactions/${id}`, {
            method: 'DELETE'
        })
        if (!response.ok) {
            throw new Error('Failed to delete transaction.')
        }
        emit('transaction-deleted')
        alert('Transaction deleted successfully!')
    } catch (error) {
        console.error(error)
        alert('Error: ' + error.message)
    }
}
</script>

<template>
    <div class="transaction-list">
        <h2>Recent Transactions</h2>
        <div v-if="transactions.length === 0" class="empty-state">
            No transactions yet. Add one using the form above!
        </div>
        <table v-else>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th>Amount</th>
                    <th>From</th>
                    <th>To</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <!-- Loop through each transaction and create a table row -->
                <tr v-for="transaction in transactions" :key="transaction.id">
                    <td>{{ formatDate(transaction.date) }}</td>
                    <td>{{ transaction.type }}</td>
                    <td>{{ transaction.description }}</td>
                    <td>{{ transaction.category }}</td>
                    <td class="amount">{{ formatCurrency(transaction.amount) }}</td>
                    <td>{{ transaction.from_account }}</td>
                    <td>{{ transaction.to_account }}</td>
                    <td>
                        <button @click="$emit('edit', transaction)" class="edit-btn">Edit</button>
                        <button @click="handleDelete(transaction.id)" class="delete-btn">X</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
.transaction-list {
    margin-top: 2rem;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}
th, td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}
th {
    background-color: #f4f4f4;
}
tr:nth-child(even) {
    background-color: #f9f9f9;
}
.amount {
    font-weight: bold;
}
.edit-btn {
    background-color: #007bff;
    margin-right: 5px;
}
.edit-btn:hover {
    background-color: #0056b3;
}
.delete-btn {
    background-color: #e74c3c;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    padding: 5px 10px;
}
.delete-btn:hover {
    background-color: #c0392b;
}
.empty-state {
    margin-top: 1rem;
    padding: 20px;
    text-align: center;
    color: #777;
    background-color: #fafafa;
    border: 1px dashed #ccc;
}
</style>
