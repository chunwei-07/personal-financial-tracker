<script setup>
import { computed } from 'vue';

const props = defineProps({
    currentPage: { type: Number, required: true },
    totalItems: { type: Number, required: true },
    itemsPerPage: { type: Number, default: 10 }
});

const emit = defineEmits(['page-changed']);

const totalPages = computed(() => {
    return Math.ceil(props.totalItems / props.itemsPerPage);
});

const isFirstPage = computed(() => props.currentPage === 1);
const isLastPage = computed(() => props.currentPage === totalPages.value);

const changePage = (newPage) => {
    if (newPage > 0 && newPage <= totalPages.value) {
        emit('page-changed', newPage);
    }
};
</script>

<template>
    <div class="pagination-controls" v-if="totalPages > 1">
        <button @click="changePage(currentPage - 1)" :disabled="isFirstPage">
            « Previous
        </button>
        <span>Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="changePage(currentPage + 1)" :disabled="isLastPage">
            Next »
        </button>
    </div>
</template>

<style scoped>
.pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 1.5rem;
}
button {
    padding: 8px 16px;
    border: 1px solid #ddd;
    background-color: #f9f9f9;
    cursor: pointer;
    border-radius: 4px;
}
button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}
span {
    font-weight: bold;
}
</style>
