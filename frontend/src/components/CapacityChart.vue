<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ result: { type: Object, default: null } })
const chartEl = ref()
let chart

function render() {
  if (!props.result || !chartEl.value) return
  chart ??= echarts.init(chartEl.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['热储能量', '电力产能'] },
    yAxis: { type: 'value', name: '数值' },
    series: [{ type: 'bar', data: [props.result.thermal_energy_gj, props.result.electrical_power_mw], itemStyle: { color: '#16a085' } }],
  })
}

watch(() => props.result, async () => { await nextTick(); render() })
onBeforeUnmount(() => chart?.dispose())
</script>

<template><div ref="chartEl" class="chart" /></template>

<style scoped>.chart { height: 320px; width: 100%; }</style>
