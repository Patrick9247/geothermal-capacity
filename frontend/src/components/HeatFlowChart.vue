<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ results: { type: Array, default: () => [] } })
const chartEl = ref()
let chart

function render() {
  if (!chartEl.value || !props.results.length) return
  chart ??= echarts.init(chartEl.value)
  chart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value) => `${value} MW` },
    grid: { left: 72, right: 28, top: 42, bottom: 78 },
    xAxis: { type: 'category', name: 'time', nameLocation: 'middle', nameGap: 52, boundaryGap: false, data: props.results.map((item) => item.time.replace('T', ' ').replace(/ (0)(\d):/, ' $2:')), axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Heat Flow (MW)' },
    series: [{ name: 'Q总', type: 'line', smooth: false, showSymbol: true, symbol: 'circle', symbolSize: 12, data: props.results.map((item) => item.q_total_mw), lineStyle: { color: '#1E3E6E', width: 3 }, itemStyle: { color: '#1E3E6E' } }],
  }, true)
}

function resize() { chart?.resize() }
watch(() => props.results, async () => { await nextTick(); render() }, { deep: true })
onMounted(async () => {
  window.addEventListener('resize', resize)
  await nextTick()
  render()
})
onBeforeUnmount(() => { window.removeEventListener('resize', resize); chart?.dispose() })
</script>

<template><div ref="chartEl" class="chart" /></template>

<style scoped>.chart { height: 400px; width: 100%; }</style>
