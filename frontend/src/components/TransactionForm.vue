<!-- Form to submit new expenses, incomes, transfers -->
<script setup>
// import { FetchableDevEnvironment } from 'vite'
import { ref, reactive, onMounted, computed } from 'vue'
// import { parseQuery } from 'vue-router'

// Defines a custom event that the component can send to parent
const emit = defineEmits(['transaction-added'])

// Reactive object to hold all form data
const form = reactive({
    type: 'Expense',
    amount: null,
    category: '',
    description: '',
    from_account: '',
    to_account: ''
})

// Pre-defined options for dropdowns
const accounts = ref([])
const expenseCategories = ref([])
const incomeCategories = ref([])
// 'Food', 'Transport', 'Salary', 'Investment', 'Groceries', 'Utilities'

// This computed property returns the correct list of categories based on the form's type
const currentCategories = computed(() => {
    return form.type === 'Expense' ? expenseCategories.value : incomeCategories.value
})

// --- API FUNCTIONS ---
const fetchAccounts = async () => {
    try {
        const response = await fetch('http://localhost:8000/accounts/')
        accounts.value = await response.json()
        if (accounts.value.length > 0) {
            form.from_account = accounts.value[0].name
            form.to_account = accounts.value[0].name
        }
    } catch (error) {
        console.error('Failed to fetch accounts:', error)
    }
}

// Function to fetch categories from backend
const fetchCategories = async () => {
    try {
        const [expRes, incRes] = await Promise.all([
            fetch('http://localhost:8000/categories/?type=Expense'),
            fetch('http://localhost:8000/categories/?type=Income')
        ])
        expenseCategories.value = await expRes.json()
        incomeCategories.value = await incRes.json()

        // Set default category
        if (currentCategories.value.length > 0) {
            form.category = currentCategories.value[0].name
        }
    } catch (error) {
        console.error('Failed to fetch categories:', error)
    }
}

// Function to add new category
const addNewCategory = async () => {
    const newCategoryName = prompt(`Enter new ${form.type} category:`)
    if (!newCategoryName || newCategoryName.trim() === '') {
        return // User cancelled or entered nothing
    }

    try {
        await fetch('http://localhost:8000/categories/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                name: newCategoryName.trim(), 
                type: form.type 
            })
        })
        // After adding, refresh the category list
        await fetchCategories()
        form.category = newCategoryName.trim()
    } catch (error) {
        console.error('Failed to add category:', error)
        alert('Could not add the new category.')
    }
}

const addNewAccount = async () => {
    const newAccountName = prompt('Enter new account name (e.g., Investment):')
    if (!newAccountName) {
        return
    }
    try {
        await fetch('http://localhost:8000/accounts/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newAccountName.trim() })
        })
        await fetchAccounts()
    } catch (error) {
        console.error('Failed to add account:', error)
    }
}

// --- LIFECYCLE HOOK ---
onMounted(() => {
    fetchAccounts()
    fetchCategories()
})

const handleSubmit = async () => {
    // Basic validation
    if (!form.amount || form.amount <= 0) {
        alert('Please enter a valid amount.')
        return
    }

    // Set from/to accounts based on type
    const payload = { ...form }
    if (form.type === 'Expense') {
        payload.to_account = null
    } else if (form.type === 'Income') {
        payload.from_account = null
    } else if (form.type === 'Transfer') {
        payload.category = 'Transfer'
    }

    try {
        await fetch('http://localhost:8000/transactions/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        emit('transaction-added')
        alert('Transaction added successfully!')
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

            <!-- Type -->
            <div class="form-group">
                <label>Type:</label>
                <select v-model="form.type">
                    <option>Expense</option>
                    <option>Income</option>
                    <option>Transfer</option>
                </select>
            </div>

            <!-- Amount -->
            <div class="form-group">
                <label>Amount:</label>
                <input type="number" step="0.01" v-model.number="form.amount" placeholder="0.00" />
            </div>

            <!-- Category (Only for Expense/Income) -->
            <div class="form-group" v-if="form.type !== 'Transfer'">
                <label>
                    {{ form.type }} Category:
                    <button type="button" @click="addNewCategory" class="add-btn" title="Add new category">+</button>
                </label>
                <select v-model="form.category">
                    <option v-for="cat in currentCategories" :key="cat.id" :value="cat.name">{{ cat.name }}</option>
                </select>
            </div>

            <!-- From Account (Only for Expense/Transfer) -->
            <div class="form-group" v-if="form.type !== 'Income'">
                <label>
                    From Account:
                    <button type="button" @click="addNewAccount" class="add-btn" title="Add new account">+</button>
                </label>
                <select v-model="form.from_account">
                    <option v-for="acc in accounts" :key="acc.id" :value="acc.name">{{ acc.name }}</option>
                </select> 
            </div>

            <!-- To Account (Only for Income/Transfer) -->
            <div class="form-group" v-if="form.type !== 'Expense'">
                <label>
                    To Account:
                    <button type="button" @click="addNewAccount" class="add-btn" title="Add new account">+</button>
                </label>
                <select v-model="form.to_account">
                    <option v-for="acc in accounts" :key="acc.id" :value="acc.name">{{ acc.name }}</option>
                </select>
            </div>

            <!-- Description -->
            <div class="form-group">
                <label>Description:</label>
                <input type="text" v-model="form.description" placeholder="Optional details" />
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
.add-btn {
    margin-left: 10px;
    margin-bottom: 2px;
    padding: 5px 5px;
    border-radius: 50%;
    border: 1px solid #ccc;
    cursor: pointer;
    width: 24px;
    height: 24px;
    background-color: #e0e0e0;
    font-weight: bold;
}
/* label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
} */
label {
    display: flex;
    align-items: center;
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
