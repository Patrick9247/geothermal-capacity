<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ result: { type: Object, default: null } })
const chartEl = ref()
let chart

function render() {
  if (!props.result || !chartEl.value) return
  chart ??= echarts.init(chartEl.value)
  chart.setOption(
    {
      tooltip: {
        trigger: 'item',
        formatter: (params) =>
          `${params.marker}${params.name}：${params.value} MW（${params.percent}%）<br/>Q总（Qw + Qs）：${props.result.q_total_mw.toFixed(4)} MW`,
      },
      legend: { bottom: 0, icon: 'circle', itemWidth: 10, itemHeight: 10 },
      title: {
        text: `${props.result.q_total_mw.toFixed(4)} MW`,
        subtext: 'Q总（Qw + Qs）',
        left: 'center',
        top: '34%',
        textStyle: { fontSize: 18, fontWeight: 600, color: '#1E3E6E' },
        subtextStyle: { fontSize: 13, color: '#64748b' },
      },
      series: [
        {
          type: 'pie',
          radius: ['42%', '68%'],
          center: ['50%', '42%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { formatter: '{b}\n{c} MW', color: '#1f2937' },
          data: [
            { name: 'Qw（地热水热流量）', value: props.result.qw_mw, itemStyle: { color: '#1E3E6E' } },
            { name: 'Qs（地热蒸汽热流量）', value: props.result.qs_mw, itemStyle: { color: '#16a085' } },
          ],
        },
      ],
    },
    true,
  )
}

function resize() {
  chart?.resize()
}

watch(() => props.result, async () => { await nextTick(); render() }, { deep: true })
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
.chart { height: 320px; width: 100%; margin-top: 8px; }
</style>
