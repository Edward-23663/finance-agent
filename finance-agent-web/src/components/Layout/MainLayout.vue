<template>
  <el-container class="main-layout">
    <AppSidebar />
    <el-container>
      <AppHeader />
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import AppSidebar from './AppSidebar.vue';
import AppHeader from './AppHeader.vue';
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  
  .main-content {
    background: #f0f2f5;
    padding: 20px;
    min-height: calc(100vh - 60px);
  }
}
</style>
