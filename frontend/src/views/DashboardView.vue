<script setup>
import { ref, onMounted } from 'vue';
import { formatCurrency } from '@/utils/formatters';

const balances = ref(null)
const isLoading = ref(true)

const fetchBalances = async () => {
    try {
        isLoading.value = true
        const response = await fetch('/accounts/balances')
        if (!response.ok) throw new Error('Failed to fetch balances')
        balances.value = await response.json()
    } catch (error) {
        console.error(error)
    } finally {
        isLoading.value = false
    }
}

onMounted(fetchBalances)
</script>

<template>
    <div class="dashboard">
        <h1>Dashboard</h1>

        <div v-if="isLoading" class="loading">Loading balances...</div>

        <div v-else-if="balances && Object.keys(balances).length > 0" class="balances-grid">
            <div v-for="(balance, account) in balances" :key="account" class="balance-card">
                <h2>{{ account }}</h2>
                <p :class="balance >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(balance) }}
                </p>
            </div>
        </div>

        <div v-else class="info-box">
            <h2>Welcome to Your Financial Tracker!</h2>
            <p>
                You have no account balances yet. To get started, you need to record your current balances.
            </p>
            <ol>
                <li>Go to the <strong>Home</strong> page.</li>
                <li>Select the transaction type <strong>Income</strong>.</li>
                <li>Choose the category <strong>"Initial Balance"</strong>.</li>
                <li>Enter your current balance for an account (e.g., Bank Account).</li>
                <li>Submit the transaction.</li>
            </ol>
            <p>Repeat this for each of your accounts (Cash, E-wallet, etc.). Your balances will then appear here!</p>
        </div>
    </div>
</template>

<style scoped>
.dashboard {
    max-width: 960px;
    margin: 2rem auto;
    padding: 0 1rem;
}
.balance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}
.balance-card {
    background-color: #f9f9f9;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}
.balance-card h2 {
    margin-top: 0;
    color: #333;
}
.balance-card p {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0;
}
.positive { color: #28a745; }
.negative { color: #e74c3c; }
.info-box {
    margin-top: 2rem;
    padding: 2rem;
    background-color: #eef7ff;
    border: 1px solid #bde0fe;
    border-radius: 8px;
}
.info-box li {
    margin-bottom: 0.5rem;
}
</style>
