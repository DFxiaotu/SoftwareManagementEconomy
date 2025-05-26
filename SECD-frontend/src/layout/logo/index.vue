<template>
  <div class="logo">
    <h2 v-show="!collapsed" class="title">MRI海扶疗效评估系统</h2>
  </div>
</template>

<script setup>
  defineProps({
    collapsed: {
      type: Boolean,
    },
  });
</script>

<style lang="less" scoped>
  .logo {
    @apply flex overflow-hidden whitespace-nowrap items-center;

    height: 64px;
    padding-left: 24px;
    line-height: 64px;

    .title {
      @apply mb-0 text-lg;

      color: var(--app-primary-color);
    }
  }
</style>
