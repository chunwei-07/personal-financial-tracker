<script setup>
import { ref, onMounted, computed } from 'vue';
import { formatCurrency } from '@/utils/formatters';
import NetWorthChart from '@/components/NetWorthChart.vue';

const balances = ref(null);
const netWorthHistory = ref([]);
const budgetStatus = ref([]);
const isLoading = ref(true);

const fetchDashboardData = async () => {
    isLoading.value = true;
    try {
        const [balanceRes, historyRes, budgetRes] = await Promise.all([
            fetch('/accounts/balances'),
            fetch('/net-worth/history'),
            fetch('/budgets/status')
        ]);
        if (!balanceRes.ok || !historyRes.ok || !budgetRes.ok ) throw new Error('Failed to fetch dashboard data');

        balances.value = await balanceRes.json();
        netWorthHistory.value = await historyRes.json();
        budgetStatus.value = await budgetRes.json();
    } catch (error) {
        console.error(error);
    } finally {
        isLoading.value = false;
    }
};

onMounted(fetchDashboardData)

const currentNetWorth = computed(() => {
    if (!balances.value) return 0;
    return Object.values(balances.value).reduce((sum, value) => sum + value, 0);
});

const netWorthChartData = computed(() => {
    const labels = netWorthHistory.value.map(item => new Date(item.date).toLocaleDateString());
    const data = netWorthHistory.value.map(item => item.value);
    return {
        labels,
        datasets: [{
            label: 'Net Worth',
            backgroundColor: 'rgba(0, 123, 255, 0.2)',
            borderColor: 'rgba(0, 123, 255, 1)',
            data,
            fill: true,
            tension: 0.1
        }]
    };
});

const getBudgetProgress = (budget) => {
    if (budget.budgeted_amount <= 0) return 0;
    return (budget.spent_amount / budget.budgeted_amount) * 100;
};
</script>

<template>
    <div class="dashboard">
        <h1>Dashboard</h1>

        <div v-if="isLoading" class="loading">Loading balances...</div>

        <div v-else>
            <!-- Net Worth Summary -->
            <div class="net-worth-summary">
                <h2>Total Net Worth</h2>
                <p :class="currentNetWorth >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(currentNetWorth) }}
                </p>
            </div>
            
            <div v-if="balances && Object.keys(balances).length > 0" class="balances-grid">
                <div v-for="(balance, account) in balances" :key="account" class="balance-card">
                    <h3>{{ account }}</h3>
                    <p :class="balance >= 0 ? 'positive' : 'negative'">
                        {{ formatCurrency(balance) }}
                    </p>
                </div>
            </div>

            <!-- Budget Card -->
            <div class="budgets-card">
                <h3>Monthly Budget Status</h3>
                <div v-if="budgetStatus.length > 0" class="budget-list">
                    <div v-for="budget in budgetStatus" :key="budget.category_name" class="budget-item">
                        <div class="budget-info">
                            <span class="category_name">{{ budget.category_name }}</span>
                            <span class="amount-info">
                                {{ formatCurrency(budget.spent_amount) }} / {{ formatCurrency(budget.budgeted_amount) }}
                            </span>
                        </div>
                        <div class="progress-bar-container">
                            <div
                                class="progress-bar"
                                :style="{ width: Math.min(getBudgetProgress(budget), 100) + '%' }"
                                :class="{ overbudget: getBudgetProgress(budget) > 100 }"
                            ></div>
                        </div>
                        <div class="remaining-info" :class="{ 'overbudget-text': budget.remaining_amount < 0 }">
                            {{ formatCurrency(budget.remaining_amount) }} {{ budget.remaining_amount >= 0 ? 'remaining' : 'over' }}
                        </div>
                    </div>
                </div>
                <p v-else>No budgets set. Go to the "Manage" page to create your first budget.</p>
            </div>

            <!-- Net Worth History Chart -->
            <div class="history-chart-card">
                <h3>Net Worth History</h3>
                <NetWorthChart v-if="netWorthHistory.length > 1" :chart-data="netWorthChartData" />
                <p v-else>Add more transactions and restart the app on different days to see your history grow.</p>
            </div>
        </div>
    </div>
</template>

<style scoped>
.dashboard {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}
.net-worth-summary {
    background-color: #007bff;
    color: white;
    text-align: center;
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
}
.net-worth-summary h2 {
    margin-top: 0;
}
.net-worth-summary p {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0;
}
.balance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
}
.balance-card {
    background-color: #f9f9f9;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}
.balance-card h3 {
    margin-top: 0;
    color: #333;
}
.balance-card p {
    font-size: 1.8rem;
    font-weight: bold;
    margin-bottom: 0;
}
.positive { color: #28a745; }
.negative { color: #dc3545; }
.net-worth-summary .positive, .net-worth-summary .negative {
    color: white;
}
.budgets-card {
    margin-top: 2rem;
    background-color: #fff;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}
.budget-item {
    margin-bottom: 1.5rem;
}
.budget-item:last-child {
    margin-bottom: 0;
}
.budget-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-weight: bold;
}
.progress-bar-container {
    width: 100%;
    background-color: #e9ecef;
    border-radius: 0.25rem;
    height: 1.2rem;
}
.progress-bar {
    height: 100%;
    background-color: #007bff;
    border-radius: 0.25rem;
    transition: width 0.3s ease-in-out;
}
.progress-bar.overbudget {
    background-color: #dc3545;
}
.remaining-info {
    text-align: right;
    margin-top: 0.25rem;
    font-size: 0.9rem;
    color: #6c757d;
}
.remaining-info.overbudget-text {
    color: #dc3545;
    font-weight: bold;
}
.history-chart-card {
    margin-top: 2rem;
    background-color: #fff;
    padding: 1.5rem;
    border-radius: 8px;
    height: 400px;
    border: 1px solid #e0e0e0;
}
</style>
