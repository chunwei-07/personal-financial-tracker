<template>
  <div class="about-container">
    <h1>About This Financial Tracker</h1>

    <div class="card">
      <p>
        This application is a personal financial trancker designed to provide a clean,
        simple, and private way to manage your finances. It was built as a personal project to
        create a self-hosted, user-friendly tool without relyingon third-party services.
      </p>
      <p>
        All of your financial data is stored locally in a private SQLite database file
        and is never sent over the internet, ensuring your information remains completely under
        your control.
      </p>
    </div>

    <div class="card">
      <h2>Technology Stack</h2>
      <p>
        This full-stack application was built using a modern, free, and open-source technology stack:
      </p>
      <ul>
        <li><strong>Backend:</strong> Built with <strong>FastAPI</strong>, a high-performance Python web framework.</li>
        <li><strong>Frontend:</strong> Powered by <strong>Vue.js</strong>, a progressive and approachable JavaScript framework.</li>
        <li><strong>Database:</strong> All data is stored in a local <strong>SQLite</strong> database, managed via <strong>SQLAlchemy</strong>.</li>
        <li><strong>Development Environment:</strong> The frontend is built and served with <strong>Vite</strong>, providing a fast and modern development experience.</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.about-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.card {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
}

h1, h2 {
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

p, li {
  line-height: 1.6;
  font-size: 1.1rem;
  color: #333;
}

ul {
  list-style-position: inside;
  padding-left: 0;
}

li {
  margin-bottom: 0.75rem;
}

strong {
  color: #0056b3;
}
</style>
