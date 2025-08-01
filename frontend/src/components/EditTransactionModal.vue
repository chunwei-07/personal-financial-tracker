<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue';

const props = defineProps({
    transaction: Object,   // transaction object to edit
    show: Boolean          // control modal visibility
});

const emit = defineEmits(['close', 'transaction-updated']);

const form = reactive({});
const accounts = ref({});
const incomeCategories = ref({});
const expenseCategories = ref({});

// Watch for changes in the transaction prop and update the form
watch(() => props.transaction, (newVal) => {
    if (newVal) {
        Object.assign(form, newVal);
    }
}, { immediate: true, deep: true });

const currentCategories = computed(() => {
    return form.type === 'Expense' ? expenseCategories.value : incomeCategories.value;
});

const fetchData = async () => {
    // Logic similar to main TransactionForm
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

const handleSubmit = async () => {
    if (!props.transaction) return;
    try {
        const response = await fetch(`/transactions/${props.transaction.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(form)
        });
        if (!response.ok) throw new Error('Failed to update transaction');
        emit('transaction-updated');
        emit('close');
    } catch (error) {
        alert(error.message);
    }
};
</script>

<template>
    <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content">
            <h2>Edit Transaction</h2>
            <form v-if="transaction" @submit.prevent="handleSubmit">
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
                    <input type="number" step="0.01" v-model.number="form.amount" />
                </div>
                <!-- Category -->
                <div class="form-group" v-if="form.type !== 'Transfer'">
                    <label>{{ form.type }} Category:</label>
                    <select v-model="form.category">
                        <option v-for="cat in currentCategories" :key="cat.id" :value="cat.name">{{ cat.name }}</option>
                    </select>
                </div>
                <!-- From/To Accounts -->
                <div class="form-group" v-if="form.type !== 'Income'">
                    <label>From Account:</label>
                    <select v-model="form.from_account">
                        <option v-for="acc in accounts" :key="acc.id" :value="acc.name">{{ acc.name }}</option>
                    </select>
                </div>
                <div class="form-group" v-if="form.type !== 'Expense'">
                    <label>To Account:</label>
                    <select v-model="form.to_account">
                        <option v-for="acc in accounts" :key="acc.id" :value="acc.name">{{ acc.name }}</option>
                    </select>
                </div>
                <!-- Description -->
                <div class="form-group">
                    <label>Description:</label>
                    <input type="text" v-model="form.description" />
                </div>

                <div class="modal-actions">
                    <button type="button" @click="$emit('close')" class="btn-cancel">Cancel</button>
                    <button type="submit" class="btn-save">Save Changes</button>
                </div>
            </form>
        </div>
    </div>
</template>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}
.form-group { 
    margin-bottom: 1rem; 
}
label { 
    display: block; 
    margin-bottom: 0.5rem; 
}
input, select { 
    width: 100%;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
}
.modal-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
.btn-cancel { 
    background-color: #6c757d;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
}
.btn-save { 
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
}
</style>
