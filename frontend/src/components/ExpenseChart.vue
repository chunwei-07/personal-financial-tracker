<!-- Vue component for pie chart -->
<script setup>
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, CategoryScale } from 'chart.js'

// Register the components to use
ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale)

// The component accepts 'chartData' as a prop from its parent
defineProps({
    chartData: {
        type: Object,
        required: true
    }
})

// Configuration options for the chart
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false
}
</script>

<template>
    <div class="chart-container">
        <h2>Monthly Expense Breakdown</h2>
        <Pie :data="chartData" :options="chartOptions" />
    </div>
</template>

<style scoped>
.chart-container {
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-top: 2rem;
    height: 400px;
}
</style>
