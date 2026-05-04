<template>
  <div class="app-layout">
    <AppHeader />
    <div class="layout-main">
      <AppSidebar />
      <main class="layout-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.layout-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.layout-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--bg-color);
}
</style>
