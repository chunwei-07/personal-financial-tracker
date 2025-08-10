<script setup>
import { ref, onMounted, computed } from 'vue';
import RecurringTransactionForm from '@/components/RecurringTransactionForm.vue';

const accounts = ref([]);
const incomeCategories = ref([]);
const expenseCategories = ref([]);
const recurringRules = ref([]);

const isFormVisible = ref(false);
const ruleToEdit = ref(null);
const budgets = ref([]);
const newBudgetValue = ref(null);

const fetchData = async () => {
    try {
        const [accRes, incCatRes, expCatRes, recRes, budRes] = await Promise.all([
            fetch('/accounts/'),
            fetch('/categories/?type=Income'),
            fetch('/categories/?type=Expense'),
            fetch('/recurring-transactions/'),
            fetch('/budgets/')
        ]);
        accounts.value = await accRes.json();
        incomeCategories.value = await incCatRes.json();
        expenseCategories.value = await expCatRes.json();
        recurringRules.value = await recRes.json();
        budgets.value = await budRes.json();
    } catch (error) {
        console.error("Failed to fetch data:", error);
    }
};

onMounted(fetchData);

const getBudgetForCategory = (categoryName) => {
    return budgets.value.find(b => b.category_name === categoryName);
};

const handleBudgetSubmit = async (categoryName, amount) => {
    if (!amount || amount < 0) {
        alert("Please enter a valid, non-negative budget amount.");
        return;
    }
    try {
        await fetch('/budgets/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category_name: categoryName, amount: amount })
        });
        fetchData();
    } catch (error) {
        alert("Failed to save budget.");
    }
};

const handleDeleteBudget = async (budgetId) => {
    if (!confirm("Are you sure you want to delete this budget?")) return;
    try {
        await fetch(`/budgets/${budgetId}`, { method: 'DELETE' });
        fetchData();
    } catch (error) {
        alert("Failed to delete budget.");
    }
};

const openForm = (rule = null) => {
    ruleToEdit.value = rule;
    isFormVisible.value = true;
};

const handleSaved = () => {
    fetchData();
};

const handleDeleteRecurring = async (ruleId) => {
    if (!confirm('Are you sure you want to delete this recurring rule?')) return;
    try {
        const response = await fetch(`/recurring-transactions/${ruleId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete rule.');
        fetchData();
    } catch (error) {
        alert(error.message);
    }
};

const handleEdit = async (item, itemType) => {
    const newName = prompt(`Enter new name for "${item.name}":`, item.name);
    if (!newName || newName.trim() === '' || newName.trim() === item.name) {
        return;
    }

    const endpoint = itemType === 'account' ? `/accounts/${item.id}` : `/categories/${item.id}`;
    const payload = {
        name: newName.trim(),
        ...(itemType === 'category' && { type: item.type })
    };

    try {
        const response = await fetch(endpoint, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Failed to update ${itemType}.`);
        }
        alert(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} updated successfully!`);
        fetchData();
    } catch (error) {
        alert(error.message);
    }
};

const handleDelete = async (item, itemType) => {
    if (!confirm(`Are you sure you want to delete "${item.name}"? This cannot be undone.`)) {
        return;
    }

    const endpoint = itemType === 'account' ? `/accounts/${item.id}` : `/categories/${item.id}`;

    try {
        const response = await fetch(endpoint, { method: 'DELETE' });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to delete ${itemType}.`);
        }
        alert(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} deleted successfully!`);
        fetchData();
    } catch (error) {
        alert(error.message);
    }
};
</script>

<template>
    <div class="manage-container">
        <h1>Manage Your App</h1>

        <!-- Recurring Rules Section -->
        <div class="list-card recurring-card">
            <div class="card-header">
                <h2>Recurring Transaction Rules</h2>
                <button @click="openForm()" class="add-new-btn">Add New Rule</button>
            </div>
            <ul>
                <li v-for="rule in recurringRules" :key="rule.id">
                    <span>Day {{ rule.day_of_month }}: {{ rule.description }} ({{ rule.amount }})</span>
                    <div class="actions">
                        <button @click="openForm(rule)" class="edit-btn">Edit</button>
                        <button @click="handleDeleteRecurring(rule.id)" class="delete-btn">Delete</button>
                    </div>
                </li>
            </ul>
            <p v-if="recurringRules.length === 0">No recurring rules defined yet.</p>
        </div>

        <div class="grid">
            <!-- Accounts Section -->
            <div class="list-card">
                <h2>Accounts</h2>
                <ul>
                    <li v-for="acc in accounts" :key="acc.id">
                        <span>{{ acc.name }}</span>
                        <div class="actions">
                            <button @click="handleEdit(acc, 'account')" class="edit-btn">Edit</button>
                            <button @click="handleDelete(acc, 'account')" class="delete-btn">Delete</button>
                        </div>
                    </li>
                </ul>
            </div>

            <!-- Expense Categories Section -->
            <div class="list-card">
                <h2>Expense Categories & Budgets</h2>
                <ul>
                    <li v-for="cat in expenseCategories" :key="cat.id" class="budget-item">
                        <div class="item-info">
                            <span>{{ cat.name }}</span>
                            <form @submit.prevent="handleBudgetSubmit(cat.name, getBudgetForCategory(cat.name)?.amount || newBudgetValue)">
                                <input
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    :placeholder="getBudgetForCategory(cat.name) ? 'Update: ' + getBudgetForCategory(cat.name).amount : 'Set Budget'"
                                    class="budget-input"
                                    @focusout="handleBudgetSubmit(cat.name, $event.target.value)"
                                />
                                <button v-if="getBudgetForCategory(cat.name)" @click.prevent="handleDeleteBudget(getBudgetForCategory(cat.name).id)" class="delete-budget-btn">X</button>
                            </form>
                        </div>
                        <div class="actions">
                            <button @click="handleEdit(cat, 'category')" class="edit-btn">Edit Name</button>
                            <!-- <button @click="handleDelete(acc, 'category')" class="delete-btn">Delete</button> -->
                        </div>
                    </li>
                </ul>
            </div>

            <!-- Income Categories Section -->
            <div class="list-card">
                <h2>Income Categories</h2>
                <ul>
                    <li v-for="cat in incomeCategories" :key="cat.id">
                        <span>{{ cat.name }}</span>
                        <div class="actions">
                            <button @click="handleEdit(cat, 'category')" class="edit-btn">Edit</button>
                            <button @click="handleDelete(cat, 'category')" class="delete-btn">Delete</button>
                        </div>
                    </li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Add modal component -->
    <RecurringTransactionForm
        :show="isFormVisible"
        :rule="ruleToEdit"
        @close="isFormVisible = false"
        @saved="handleSaved"
    />
</template>

<style scoped>
.manage-container {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}
.recurring-card {
    grid-column: 1 / -1;
    margin-bottom: 2rem;
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 0.5rem;
    margin-bottom: 0.5rem;
}
.card-header h2 {
    border: none;
    padding: 0;
    margin: 0;
}
.budget-item {
    flex-wrap: wrap;
}
.item-info {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-grow: 1;
}
.budget-item form {
    display: flex;
    align-items: center;
}
.budget-input {
    width: 100px;
    padding: 4px 8px;
}
.delete-budget-btn {
    background-color: transparent;
    color: #dc3545;
    border: 1px solid #dc3545;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    cursor: pointer;
    margin-left: 5px;
    line-height: 1;
}
.add-new-btn {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}
.list-card {
    background-color: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1.5rem;
}
.list-card h2 {
    margin-top: 0;
    padding-bottom: 0.5rem;
}
ul {
    list-style: none;
    padding: 0;
}
li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid #f0f0f0;
}
li:last-child {
    border-bottom: none;
}
.actions button {
    margin-left: 0.5rem;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    color: white;
}
.edit-btn {
    background-color: #007bff;
}
.edit-btn:hover {
    background-color: #0056b3;
}
.delete-btn {
    background-color: #dc3545;
}
.delete-btn:hover {
    background-color: #c82333;
}
</style>

