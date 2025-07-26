<!-- Form to submit new expenses, incomes, transfers -->
<script setup>
import { ref, reactive } from 'vue'

// Defines a custom event that the component can send to parent
const emit = defineEmits(['transaction-added'])

// Reactive object to hold all form data
const form = reactive({
    type: 'Expense',
    amount: null,
    category: 'Food',
    description: '',
    from_account: 'Bank Account',
    to_account: null
})

// Pre-defined options for dropdowns
const accounts = ref(['Cash', 'Bank Account', 'Touch and Go E-wallet'])
const categories = ref(['Food', 'Transport', 'Salary', 'Investment', 'Groceries', 'Utilities'])

const resetForm = () => {
    form.amount = null
    form.description = ''
}

const handleSubmit = async () => {
    // Basic validation
    if (!form.amount || form.amount <= 0) {
        alert('Please enter a valid amount.')
        return
    }

    // Set from/to accounts based on type
    if (form.type === 'Expense') {
        form.to_account = null
    } else if (form.type === 'Income') {
        form.from_account = null
    }

    try {
        const response = await fetch('http://localhost:8000/transactions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(form)
        })

        if (!response.ok) {
            throw new Error('Failed to add transaction.')
        }

        // Emit the event to notify the parent component
        emit('transaction-added')
        alert('Transaction added successfully!')
        resetForm()
    } catch (error) {
        console.error(error)
        alert('Error: ' + error.message)
    }
}
</script>

<template>
    <div class="form-container">
        <h2>Add New Transaction</h2>

        <form @submit.prevent="handleSubmit">
            <div class="form-group">
                <label>Type:</label>
                <select v-model="form.type">
                    <option>Expense</option>
                    <option>Income</option>
                    <option>Transfer</option>
                </select>
            </div>

            <div class="form-group">
                <label>Amount:</label>
                <input type="number" step="0.01" v-model.number="form.amount" placeholder="0.00" />
            </div>

            <div class="form-group">
                <label>Category:</label>
                <select v-model="form.category">
                    <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
            </div>

            <div class="form-group">
                <label>Description:</label>
                <input type="text" v-model="form.description" placeholder="e.g., Lunch with colleagues" />
            </div>

            <!-- Conditional From/To Account fields -->
            <div class="form-group" v-if="form.type !== 'Income'">
                <label>From Account:</label>
                <select v-model="form.from_account">
                    <option v-for="acc in accounts" :key="acc" :value="acc">{{ acc }}</option>
                </select> 
            </div>

            <div class="form-group" v-if="form.type !== 'Expense'">
                <label>To Account:</label>
                <select v-model="form.to_account">
                    <option v-for="acc in accounts" :key="acc" :value="acc">{{ acc }}</option>
                </select>
            </div>

            <button type="submit">Add Transaction</button>
        </form>
    </div>
</template>

<style scoped>
.form-container {
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.form-group {
    margin-bottom: 15px;
}
label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}
input, select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}
button {
    width: 100%;
    padding: 10px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}
button:hover {
    background-color: #218838;
}
</style>
