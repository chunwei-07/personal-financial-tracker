<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue';

const props = defineProps({
    show: Boolean,
    rule: { type: Object, default: null }
});

const emit = defineEmits(['close', 'saved']);

const form = reactive({
    day_of_month: 1,
    type: 'Expense',
    amount: null,
    category: '',
    description: '',
    from_account: '',
    to_account: ''
});

const accounts = ref([]);
const incomeCategories = ref([]);
const expenseCategories = ref([]);

const isEditMode = computed(() => !!props.rule);
const formTitle = computed(() => isEditMode.value ? 'Edit Recurring Rule' : 'Add New Recurring Rule');

// This watcher pre-fills the form when entering edit mode or resets it for create mode
watch(() => props.show, (newVal) => {
    if (newVal) {
        if (isEditMode.value) {
            Object.assign(form, props.rule);
        } else {
            // Reset form for new entry
            Object.assign(form, {
                day_of_month: 1, type: 'Expense', amount: null, description: '',
                category: expenseCategories.value.length > 0 ? expenseCategories.value[0].name : '',
                from_account: accounts.value.length > 0 ? accounts.value[0].name : '',
                to_account: accounts.value.length > 0 ? accounts.value[0].name : ''
            });
        }
    }
});

const currentCategories = computed(() => form.type === 'Expense' ? expenseCategories.value : incomeCategories.value);

// Fetch dropdown data when component is created
onMounted(async () => {
    try {
        const [accRes, incCatRes, expCatRes] = await Promise.all([
            fetch('/accounts/'), fetch('/categories/?type=Income'), fetch('/categories/?type=Expense')
        ]);
        accounts.value = await accRes.json();
        incomeCategories.value = await incCatRes.json();
        expenseCategories.value = await expCatRes.json();
    } catch (error) { console.error("Failed to fetch form data:", error); }
});

const handleSubmit = async () => {
    const endpoint = isEditMode.value ? `/recurring-transactions/${props.rule.id}` : '/recurring-transactions/';
    const method = isEditMode.value ? 'PUT' : 'POST';

    try {
        const response = await fetch(endpoint, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(form)
        });
        if (!response.ok) throw new Error('Failed to save the rule.');
        emit('saved');
        emit('close');
    } catch (error) { alert(error.message); }
};
</script>

<template>
    <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content">
            <h2>{{ formTitle }}</h2>
            <form @submit.prevent="handleSubmit">
                <!-- Form fields are very similar to our other forms -->
                <div class="form-group">
                    <label>Day of Month (1-31):</label>
                    <input type="number" min="1" max="31" v-model.number="form.day_of_month" required/>
                </div>
                <div class="form-group">
                    <label>Type:</label>
                    <select v-model="form.type" required>
                        <option>Expense</option>
                        <option>Income</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Amount:</label>
                    <input type="number" step="0.01" v-model.number="form.amount" required placeholder="0.00" />
                </div>
                <div class="form-group">
                    <label>Category:</label>
                    <select v-model="form.category" required>
                        <option v-for="cat in currentCategories" :key="cat.id" :value="cat.name">{{ cat.name }}</option>
                    </select>
                </div>
                <div class="form-group" v-if="form.type !== 'Income'">
                    <label>From Account:</label>
                    <select v-model="form.from_account" required>
                        <option v-for="acc in accounts" :key="acc.id" :value="acc.name">{{ acc.name }}</option>
                    </select>
                </div>
                <div class="form-group" v-if="form.type !== 'Expense'">
                    <label>To Account:</label>
                    <select v-model="form.to_account" required>
                        <option v-for="acc in accounts" :key="acc.id" :value="acc.name">{{ acc.name }}</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Description:</label>
                    <input type="text" v-model="form.description" required placeholder="e.g., Monthly Rent" />
                </div>
                <div class="modal-actions">
                    <button type="button" @click="$emit('close')" class="btn-cancel">Cancel</button>
                    <button type="submit" class="btn-save">Save Rule</button>
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
    background: #fff;
    padding: 2rem;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
}
.form-group {
    margin-bottom: 1rem;
}
.form-group label {
    display: block;
    margin-bottom: 0.5rem;
}
.form-group input, select {
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
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
}
.btn-save {
    background-color: #007bff;
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
}
</style>
