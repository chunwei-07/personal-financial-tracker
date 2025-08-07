<script setup>
import { ref, onMounted, computed } from 'vue';
import { formatCurrency } from '@/utils/formatters';
import NetWorthChart from '@/components/NetWorthChart.vue';

const balances = ref(null);
const netWorthHistory = ref([]);
const isLoading = ref(true);

const fetchDashboardData = async () => {
    isLoading.value = true;
    try {
        const [balanceRes, historyRes] = await Promise.all([
            fetch('/accounts/balances'),
            fetch('/net-worth/history')
        ]);
        if (!balanceRes.ok || !historyRes.ok) throw new Error('Failed to fetch dashboard data');

        balances.value = await balanceRes.json();
        netWorthHistory.value = await historyRes.json();
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
.history-chart-card {
    margin-top: 2rem;
    background-color: #fff;
    padding: 1.5rem;
    border-radius: 8px;
    height: 400px;
    border: 1px solid #e0e0e0;
}
</style>
