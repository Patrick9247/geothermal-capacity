<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { calculateHeatFlow, deleteHeatFlowRecord, getHeatFlowRecords, saveHeatFlowInputs } from '../api/calculations'
import HeatFlowBarChart from './HeatFlowBarChart.vue'
import HeatFlowChart from './HeatFlowChart.vue'
import HeatFlowPieChart from './HeatFlowPieChart.vue'

let nextRowId = 2
const loading = ref(false)
const results = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const inputsReady = ref(false)
const persistingInputs = ref(false)
const fileInput = ref()
let persistTimer
let lastPersistedSignature = ''
const rows = ref([
  { id: null, rowId: 1, time: '2026-08-05 09:00', p1_mpa: 1, t1_c: 180, p2_mpa: 0.5, t2_c: 150, w1_kg_s: 25, w2_kg_s: 8 },
])

const pagedRows = computed(() => rows.value.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value))
const latestResult = computed(() => results.value.at(-1))

function addRow() {
  const last = rows.value.at(-1)
  rows.value.push({ ...last, id: null, rowId: nextRowId++, time: last?.time || '' })
  currentPage.value = Math.ceil(rows.value.length / pageSize.value)
}

async function removeRow(rowId) {
  if (rows.value.length === 1) return ElMessage.warning('至少保留一条数据')
  const target = rows.value.find((row) => row.rowId === rowId)
  try {
    if (target?.id) await deleteHeatFlowRecord(target.id)
    rows.value = rows.value.filter((row) => row.rowId !== rowId)
  } catch (error) {
    return ElMessage.error(error.response?.data?.detail || '删除失败')
  }
  const maxPage = Math.ceil(rows.value.length / pageSize.value)
  if (currentPage.value > maxPage) currentPage.value = maxPage
  results.value = []
}

function rowNumber(index) { return (currentPage.value - 1) * pageSize.value + index + 1 }

function inputsSignature() {
  return JSON.stringify(rows.value.map(({ id, rowId, ...point }) => point))
}

function currentMinute() {
  const now = new Date()
  const pad = (value) => String(value).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`
}

function fillMissingTimes() {
  rows.value.forEach((row) => {
    if (!row.time) row.time = currentMinute()
  })
}

const importedColumns = [
  ['时间', 'time'], ['P1', 'p1_mpa'], ['T1', 't1_c'], ['P2', 'p2_mpa'],
  ['T2', 't2_c'], ['W1', 'w1_kg_s'], ['W2', 'w2_kg_s'],
]

function downloadTemplate() {
  const example = ['2026/8/5 0:00', 0.64, 161, 0.63, 160, 7.5, 44]
  const csv = `\uFEFF${importedColumns.map(([label]) => label).join(',')}\n${example.join(',')}\n`
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = '地热产能计算导入模板.csv'
  link.click()
  URL.revokeObjectURL(url)
}

function parseCsvLine(line) {
  return line.match(/("(?:[^"]|"")*"|[^,]*)(?:,|$)/g)?.map((cell) => cell.replace(/,$/, '').replace(/^"|"$/g, '').replace(/""/g, '"')) || []
}

function normalizeTime(value) {
  if (!value) return ''
  const match = String(value).trim().match(/(\d{4})[\/\-.](\d{1,2})[\/\-.](\d{1,2})(?:[ T]+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?/)
  if (!match) return String(value).trim()
  const [, y, m, d, h = '00', min = '00', s = '00'] = match
  const pad = (n) => String(n).padStart(2, '0')
  return `${y}-${pad(m)}-${pad(d)} ${pad(h)}:${pad(min)}`
}

async function importData(event) {
  const [file] = event.target.files
  event.target.value = ''
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.csv')) return ElMessage.warning('当前仅支持 CSV 格式，请使用下载的模板导入')
  try {
    const lines = (await file.text()).replace(/^\uFEFF/, '').split(/\r?\n/).filter((line) => line.trim())
    if (lines.length < 2) return ElMessage.warning('模板中没有可导入的数据行')
    const headers = parseCsvLine(lines[0]).map((header) => header.trim())
    const indexes = importedColumns.map(([label, key]) => ({ key, index: headers.indexOf(label) }))
    if (indexes.some(({ index }) => index < 0)) return ElMessage.error('导入文件表头不符合模板要求')
    const importedRows = lines.slice(1).map((line) => {
      const values = parseCsvLine(line)
      const row = { id: null, rowId: nextRowId++ }
      indexes.forEach(({ key, index }) => { row[key] = key === 'time' ? normalizeTime(values[index]) : Number(values[index]) })
      return row
    }).filter((row) => Object.values(row).some((value) => value !== '' && value !== 0 && value !== null))
    if (!importedRows.length) return ElMessage.warning('未读取到有效数据')
    rows.value.push(...importedRows)
    currentPage.value = Math.ceil(rows.value.length / pageSize.value)
    ElMessage.success(`已导入 ${importedRows.length} 条数据`)
  } catch {
    ElMessage.error('导入失败，请检查 CSV 文件内容')
  }
}

function formatMinute(value) {
  if (!value) return '-'
  const text = String(value).replace('T', ' ')
  const [date, clock = ''] = text.split(' ')
  const [hour = '0', minute = '00'] = clock.split(':')
  return `${date} ${Number(hour)}:${minute}`
}

async function calculate() {
  fillMissingTimes()
  clearTimeout(persistTimer)
  loading.value = true
  try {
    const { data } = await calculateHeatFlow(rows.value.map(({ rowId, ...point }) => point))
    results.value = data.results
    data.results.forEach((result, index) => { rows.value[index].id = result.id })
    lastPersistedSignature = inputsSignature()
    ElMessage.success(`已完成 ${data.results.length} 条数据计算`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '计算失败，请检查参数')
  } finally { loading.value = false }
}

async function persistInputs() {
  if (!inputsReady.value || loading.value || persistingInputs.value) return
  fillMissingTimes()
  const signature = inputsSignature()
  if (signature === lastPersistedSignature) return
  persistingInputs.value = true
  try {
    const { data } = await saveHeatFlowInputs(rows.value.map(({ rowId, ...point }) => point))
    data.ids.forEach((id, index) => { rows.value[index].id = id })
    lastPersistedSignature = signature
    results.value = []
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '输入参数保存失败')
  } finally { persistingInputs.value = false }
}

async function loadRecords() {
  loading.value = true
  try {
    const { data } = await getHeatFlowRecords()
    if (!data.length) return
    rows.value = data.map((record) => ({ ...record, rowId: nextRowId++ }))
    results.value = data.filter((record) => record.q_total_mw !== null).map((record) => ({
      id: record.id, time: record.time, qw_mw: record.qw_mw, qs_mw: record.qs_mw, q_total_mw: record.q_total_mw,
    }))
  } catch (error) { ElMessage.error(error.response?.data?.detail || '历史计算记录加载失败') }
  finally { loading.value = false; lastPersistedSignature = inputsSignature(); inputsReady.value = true }
}

onMounted(loadRecords)
onBeforeUnmount(() => clearTimeout(persistTimer))
watch(rows, () => {
  if (!inputsReady.value || loading.value) return
  if (inputsSignature() === lastPersistedSignature) return
  clearTimeout(persistTimer)
  persistTimer = setTimeout(persistInputs, 700)
}, { deep: true })
</script>

<template>
  <el-card class="formula-card">
    <template #header><div class="card-header"><span>计算公式与说明</span></div></template>
    <div class="formula-grid">
      <div class="formula-item">
        <div class="formula-name">地热水热流量 Q<sub>W</sub></div>
        <div class="formula-body">Q<sub>W</sub> = W<sub>1</sub> × h<sub>W</sub>(T<sub>1</sub>, P<sub>1</sub>) / 1000</div>
        <div class="formula-unit">单位：MW</div>
      </div>
      <div class="formula-item">
        <div class="formula-name">地热蒸汽热流量 Q<sub>s</sub></div>
        <div class="formula-body">Q<sub>s</sub> = W<sub>2</sub> × h<sub>s</sub>(T<sub>2</sub>, P<sub>2</sub>) / 1000</div>
        <div class="formula-unit">单位：MW</div>
      </div>
      <div class="formula-item">
        <div class="formula-name">总产能 Q<sub>总</sub></div>
        <div class="formula-body">Q<sub>总</sub> = Q<sub>W</sub> + Q<sub>s</sub></div>
        <div class="formula-unit">单位：MW</div>
      </div>
    </div>
    <table class="symbol-table">
      <thead>
        <tr><th>符号</th><th>含义</th><th>单位</th><th>输入/输出</th></tr>
      </thead>
      <tbody>
        <tr><td>Q<sub>W</sub></td><td>地热水热流量</td><td>MW</td><td>输出</td></tr>
        <tr><td>Q<sub>s</sub></td><td>地热蒸汽热流量</td><td>MW</td><td>输出</td></tr>
        <tr><td>Q<sub>总</sub></td><td>地热井总产能（Q<sub>W</sub> + Q<sub>s</sub>）</td><td>MW</td><td>输出</td></tr>
        <tr><td>W<sub>1</sub></td><td>地热水质量流量</td><td>kg/s</td><td>输入</td></tr>
        <tr><td>W<sub>2</sub></td><td>地热蒸汽质量流量</td><td>kg/s</td><td>输入</td></tr>
        <tr><td>h<sub>W</sub></td><td>地热水比焓</td><td>kJ/kg</td><td>库函数计算</td></tr>
        <tr><td>h<sub>s</sub></td><td>地热蒸汽比焓</td><td>kJ/kg</td><td>库函数计算</td></tr>
        <tr><td>T<sub>1</sub>、P<sub>1</sub></td><td>地热水温度、压力</td><td>℃、MPa</td><td>输入</td></tr>
        <tr><td>T<sub>2</sub>、P<sub>2</sub></td><td>地热蒸汽温度、压力</td><td>℃、MPa</td><td>输入</td></tr>
      </tbody>
    </table>
    <el-alert type="info" :closable="false" class="seuif97-note">
      <template #title>焓值由 seuif97 库计算</template>
      <p>h = seuif97.pt2h(P, T)，即根据压力 P（MPa）和温度 T（℃）求得水/水蒸气的比焓 h（kJ/kg）。seuif97 是基于 IAPWS-IF97 国际标准的水和水蒸气热力性质计算库；流量与焓的乘积 W × h 单位为 kW（kg/s × kJ/kg），除以 1000 后即为 MW。当压力或温度超出 seuif97 的有效计算范围时，计算会返回“压力或温度超出 seuif97 的有效计算范围”的提示。</p>
    </el-alert>
  </el-card>

  <el-card>
    <template #header><div class="card-header"><span>地热产能计算</span>
      <div><input ref="fileInput" class="file-input" type="file" accept=".csv,text/csv" @change="importData" />
        <el-button @click="fileInput?.click()">导入数据</el-button>
        <el-button @click="downloadTemplate">下载导入数据模板</el-button>
        <el-button @click="addRow">新增一行</el-button>
        <el-button type="primary" :loading="loading" @click="calculate">计算</el-button>
      </div>
    </div>
  </template>
    <el-table :data="pagedRows" border class="input-table">
      <el-table-column label="序号" width="72"><template #default="{ $index }">{{ rowNumber($index) }}</template></el-table-column>
      <el-table-column label="时间" min-width="175"><template #default="{ row }"><el-date-picker v-model="row.time" type="datetime" value-format="YYYY-MM-DD HH:mm" format="YYYY-MM-DD H:mm" /></template></el-table-column>
      <el-table-column label="P1（地热水压力 MPa）" min-width="155"><template #default="{ row }"><el-input-number v-model="row.p1_mpa" :min="0.001" :precision="3" /></template></el-table-column>
      <el-table-column label="T1（地热水温度 ℃）" min-width="155"><template #default="{ row }"><el-input-number v-model="row.t1_c" :precision="2" /></template></el-table-column>
      <el-table-column label="P2（地热蒸汽压力 MPa）" min-width="165"><template #default="{ row }"><el-input-number v-model="row.p2_mpa" :min="0.001" :precision="3" /></template></el-table-column>
      <el-table-column label="T2（地热蒸汽温度 ℃）" min-width="165"><template #default="{ row }"><el-input-number v-model="row.t2_c" :precision="2" /></template></el-table-column>
      <el-table-column label="W1（地热水质量流量 kg/s）" min-width="175"><template #default="{ row }"><el-input-number v-model="row.w1_kg_s" :min="0" :precision="3" /></template></el-table-column>
      <el-table-column label="W2（地热蒸汽质量流量 kg/s）" min-width="185"><template #default="{ row }"><el-input-number v-model="row.w2_kg_s" :min="0" :precision="3" /></template></el-table-column>
      <el-table-column label="操作" fixed="right" width="78"><template #default="{ row }"><el-button link type="danger" @click="removeRow(row.rowId)">删除</el-button></template></el-table-column>
    </el-table>
    <div class="pagination"><el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" :total="rows.length" @size-change="currentPage = 1" /></div>
  </el-card>

  <template v-if="results.length">
    <el-card class="result-card" header="计算结果（最新时间点）">
      <el-row :gutter="16"><el-col :xs="24" :sm="8"><el-statistic title="Qw（地热水热流量）" :value="latestResult.qw_mw" :precision="4"><template #suffix>MW</template></el-statistic></el-col><el-col :xs="24" :sm="8"><el-statistic title="Qs（地热蒸汽热流量）" :value="latestResult.qs_mw" :precision="4"><template #suffix>MW</template></el-statistic></el-col><el-col :xs="24" :sm="8"><el-statistic title="Q总（Qw + Qs）" :value="latestResult.q_total_mw" :precision="4"><template #suffix>MW</template></el-statistic></el-col></el-row>
      <HeatFlowPieChart :result="latestResult" />
    </el-card>
    <el-card class="result-card" header="各时间点计算结果">
      <el-table :data="results" border max-height="320"><el-table-column label="时间" min-width="180"><template #default="{ row }">{{ formatMinute(row.time) }}</template></el-table-column><el-table-column prop="qw_mw" label="Qw（MW）" /><el-table-column prop="qs_mw" label="Qs（MW）" /><el-table-column prop="q_total_mw" label="Q总（MW）" /></el-table>
      <HeatFlowBarChart :results="results" />
    </el-card>
    <el-card class="result-card" header="地热产能趋势"><HeatFlowChart :results="results" /></el-card>
  </template>
</template>

<style scoped>
.card-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.formula-card { margin-bottom: 20px; }
.formula-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
@media (max-width: 900px) { .formula-grid { grid-template-columns: 1fr; } }
.formula-item { background: #f4f7f6; border-left: 4px solid #1E3E6E; border-radius: 6px; padding: 12px 14px; }
.formula-name { font-weight: 600; color: #1E3E6E; margin-bottom: 6px; font-size: 13px; }
.formula-body { font-size: 16px; font-family: "Cambria Math", "Times New Roman", serif; color: #1f2937; }
.formula-unit { font-size: 12px; color: #64748b; margin-top: 4px; }
.symbol-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 14px; }
.symbol-table th, .symbol-table td { border: 1px solid #e5e7eb; padding: 6px 10px; text-align: left; }
.symbol-table th { background: #f4f7f6; font-weight: 600; white-space: nowrap; }
.symbol-table td:first-child { text-align: center; font-family: "Cambria Math", "Times New Roman", serif; white-space: nowrap; }
.seuif97-note { line-height: 1.6; }
.seuif97-note p { margin: 4px 0 0; font-size: 13px; }
.file-input { display: none; }
.input-table { width: 100%; }
.input-table :deep(.el-input-number), .input-table :deep(.el-date-editor) { width: 100%; }
.pagination { display: flex; justify-content: flex-end; margin-top: 18px; }
.result-card { margin-top: 20px; }
</style>
