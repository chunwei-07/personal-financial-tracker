<!-- Frame of the whole application -->
<script setup>
// Import two things from Vue Router
// RouterLink: Create nav link
// RouterView: Placeholder where pages will be displayed
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <RouterLink to="/manage">Manage</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav>
    </div>
  </header>

  <!-- Vue Router will render correct page component here -->
  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
  background-color: #f5f5f5;
  padding: 0 2rem;
  border-bottom: 1px solid #e0e0e0;
}
nav {
  width: 100%;
  font-size: 1rem;
  text-align: left;
  margin-top: 1rem;
  margin-bottom: 1rem;
}
nav a.router-link-exact-active {
  color: var(--color-text);
  font-weight: bold;
}
nav a.router-link-exact-active:hover {
  background-color: transparent;
}
nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}
nav a:first-of-type {
  border: 0;
}
</style>