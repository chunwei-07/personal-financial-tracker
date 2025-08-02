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
    <Pie :data="chartData" :options="chartOptions" />
</template>

<style scoped>
</style>
