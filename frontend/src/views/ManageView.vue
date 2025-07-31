<script setup>
import { ref, onMounted } from 'vue';

const accounts = ref([]);
const incomeCategories = ref([]);
const expenseCategories = ref([]);

const fetchData = async () => {
    try {
        const [accRes, incCatRes, expCatRes] = await Promise.all([
            fetch('/accounts/'),
            fetch('/categories/?type=Income'),
            fetch('/categories/?type=Expense')
        ]);
        accounts.value = await accRes.json();
        incomeCategories.value = await incCatRes.json();
        expenseCategories.value = await expCatRes.json();
    } catch (error) {
        console.error("Failed to fetch data:", error);
    }
};

onMounted(fetchData);

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
        <h1>Manage Accounts & Categories</h1>

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
                <h2>Expense Categories</h2>
                <ul>
                    <li v-for="cat in expenseCategories" :key="cat.id">
                        <span>{{ cat.name }}</span>
                        <div class="actions">
                            <button @click="handleEdit(cat, 'category')" class="edit-btn">Edit</button>
                            <button @click="handleDelete(cat, 'category')" class="delete-btn">Delete</button>
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
.list-card {
    background-color: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1.5rem;
}
.list-card h2 {
    margin-top: 0;
    border-bottom: 2px solid #f0f0f0;
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

