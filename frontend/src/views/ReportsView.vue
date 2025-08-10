<script setup>
import { ref, reactive, computed, watch } from 'vue';
import TransactionList from '@/components/TransactionList.vue';
import ExpenseChart from '@/components/ExpenseChart.vue';
import TrendChart from '@/components/TrendChart.vue';
import PaginationControls from '@/components/PaginationControls.vue';

// --- STATE ---
const filters = reactive({
    type: 'Expense',
    startDate: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
});

const transactions = ref([]);
const categorySummary = ref({});
const monthlySummary = ref({});
const isLoading = ref(false);

const currentPage = ref(1);
const itemsPerPage = ref(10);
const totalTransactions = ref(0);

// --- API FUNCTIONS ---
const fetchData = async () => {
    isLoading.value = true;

    // Calculate skip for pagination
    const skip = (currentPage.value - 1) * itemsPerPage.value;

    const params = new URLSearchParams({
        start_date: filters.startDate,
        end_date: filters.endDate,
        type: filters.type,
        skip: skip,
        limit: itemsPerPage.value
    }).toString();

    try {
        const [transRes, catRes, monthRes] = await Promise.all([
            fetch(`/transactions/?${params}`),
            fetch(`/transactions/summary/by-category?${params}`),
            fetch(`/transactions/summary/by-month?${params}`)
        ]);

        const transData = await transRes.json();
        transactions.value = transData.transactions;
        totalTransactions.value = transData.total_count;

        categorySummary.value = await catRes.json();
        monthlySummary.value = await monthRes.json();

    } catch (error) {
        console.error("Failed to fetch report data:", error);
    } finally {
        isLoading.value = false;
    }
};

// --- COMPUTED PROPERTIES FOR CHARTS ---
const categoryChartData = computed(() => ({
    labels: Object.keys(categorySummary.value),
    datasets: [{
        backgroundColor: [
        '#41B883', '#E46651', '#00D8FF', '#DD1B16', '#F4D03F', '#5D6D7E',
        '#F39C12', '#8E44AD', '#3498DB', '#1ABC9C', '#2ECC71', '#E74C3C'
        ],
        data: Object.values(categorySummary.value)
    }]
}));

const monthlyChartData = computed(() => ({
    labels: Object.keys(monthlySummary.value),
    datasets: [{
        label: `${filters.type} Trend`,
        backgroundColor: '#007bff',
        data: Object.values(monthlySummary.value)
    }]
}));

// --- HANDLER ---
const handlePageChange = (newPage) => {
    currentPage.value = newPage;
};

// --- WATCHER ---
// This watches the 'filters' object and calls fetchData whenever a filter is changed.
watch (filters, () => {
    // If filters change, always go back to the first page
    if (currentPage.value !== 1) {
        currentPage.value = 1;
    } else {
        fetchData();
    }
}, { immediate: true, deep: true });

watch(currentPage, fetchData);

</script>

<template>
    <div class="reports-container">
        <h1>Reports & Analysis</h1>

        <div class="filters-card">
            <h2>Filters</h2>
            <div class="filter-controls">
                <div class="form-group">
                    <label for="type">Transaction Type</label>
                    <select id="type" v-model="filters.type">
                        <option>Expense</option>
                        <option>Income</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="startDate">Start Date</label>
                    <input type="date" id="startDate" v-model="filters.startDate" />
                </div>
                <div class="form-group">
                    <label for="endDate">End Date</label>
                    <input type="date" id="endDate" v-model="filters.endDate" />
                </div>
            </div>
        </div>

        <div v-if="isLoading" class="loading-state">Loading Report...</div>

        <div v-else class="results-container">
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>{{ filters.type }} Breakdown by Category</h3>
                    <ExpenseChart v-if="Object.keys(categorySummary).length > 0" :chart-data="categoryChartData" />
                    <p v-else>No data for this period.</p>
                </div>
                <div class="chart-card">
                    <h3>{{ filters.type }} Trend by Month</h3>
                    <TrendChart v-if="Object.keys(monthlySummary).length > 0" :chart-data="monthlyChartData" />
                    <p v-else>No data for this period.</p>
                </div>
            </div>

            <div class="list-area">
                <h3>Filtered Transactions</h3>
                <TransactionList :transactions="transactions" @transaction-deleted="fetchData" />
                <PaginationControls 
                    v-if="transactions.length > 0"
                    :current-page="currentPage"
                    :total-items="totalTransactions"
                    :items-per-page="itemsPerPage"
                    @page-changed="handlePageChange"
                />
                <p v-if="transactions.length === 0 && !isLoading">No transactions match the selected filters.</p>
            </div>
        </div>
    </div>
</template>

<style scoped>
.reports-container {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}
.filters-card {
    background-color: #fff;
    padding: 1.5rem;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin-bottom: 2rem;
}
.filter-controls {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
}
.form-group {
    display: flex;
    flex-direction: column;
}
.form-group label {
    margin-bottom: 0.5rem;
    font-weight: bold;
}
.form-group input, .form-group select {
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
}
.loading-state {
    text-align: center;
    padding: 2rem;
    font-size: 1.2rem;
}
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}
.chart-card {
    background-color: #f9f9f9;
    padding: 1.5rem;
    border-radius: 8px;
    height: 400px;
}
.chart-card p {
    text-align: center;
    margin-top: 2rem;
}
.list-area {
    margin-top: 3rem;
}
</style>
