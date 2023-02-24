<script setup lang="ts">
import type { ChannelData } from '@/protocol';
import { ref, watch, computed } from 'vue';

const props = defineProps<{
  channels: ChannelData[],
}>()

const table = ref<HTMLElement>(undefined!)

const timestamps = computed(() => [...props.channels[0].timestamps].reverse())

// watch(table, () => console.log(table.scrollTop))
</script>

<template>
  <i-table class="scroll-table" ref="table">
    <thead>
      <tr>
        <th>Timestamp</th>
        <th v-for="channel in channels">
          {{ channel.meta?.name ?? channel.key }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="ts, i in timestamps" :key="timestamps.length - i">
        <td>{{ ts.toISOString() }}</td>
        <td v-for="channel in channels">
          <code>{{ channel.series[0][i] }}</code>
        </td>
      </tr>
    </tbody>
  </i-table>
</template>

<style scoped>
.scroll-table {
  max-height: 435px;
  overflow-x: hidden;
  overflow-y: auto;
}

.scroll-table thead th {
  top: 0;
  position: sticky;
}

.scroll-table tbody tr {
  animation: slide-down 0.4s ease;
}

@keyframes slide-down {
    0% {
        opacity: 0;
        transform: translateY(-20px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
