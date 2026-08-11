<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ results: { type: Array, default: () => [] } })
const chartEl = ref()
let chart

function formatTime(value) {
  return String(value).replace('T', ' ').replace(/ (0)(\d):/, ' $2:')
}

function render() {
  if (!chartEl.value || !props.results.length) return
  chart ??= echarts.init(chartEl.value)
  chart.setOption(
    {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        valueFormatter: (value) => `${value} MW`,
      },
      legend: { bottom: 0, icon: 'circle', itemWidth: 10, itemHeight: 10 },
      grid: { left: 64, right: 24, top: 40, bottom: 78 },
      xAxis: {
        type: 'category',
        name: 'time',
        nameLocation: 'middle',
        nameGap: 52,
        boundaryGap: true,
        data: props.results.map((item) => formatTime(item.time)),
        axisLabel: { rotate: 30 },
      },
      yAxis: { type: 'value', name: 'MW' },
      series: [
        {
          name: 'Qw',
          type: 'bar',
          data: props.results.map((item) => item.qw_mw),
          itemStyle: { color: '#1E3E6E', borderRadius: [3, 3, 0, 0] },
          barMaxWidth: 28,
        },
        {
          name: 'Qs',
          type: 'bar',
          data: props.results.map((item) => item.qs_mw),
          itemStyle: { color: '#16a085', borderRadius: [3, 3, 0, 0] },
          barMaxWidth: 28,
        },
      ],
    },
    true,
  )
}

function resize() {
  chart?.resize()
}

watch(() => props.results, async () => { await nextTick(); render() }, { deep: true })
onMounted(async () => {
  window.addEventListener('resize', resize)
  await nextTick()
  render()
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
</script>

<template>
  <div ref="chartEl" class="chart" />
</template>

<style scoped>
.chart { height: 400px; width: 100%; }
</style>
