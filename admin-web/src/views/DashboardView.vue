<template>
  <div class="dashboard">

    <!-- KPI 卡片 -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6" v-for="k in kpiCards" :key="k.label">
        <div class="kpi-card" :style="{ borderTop: `4px solid ${k.color}`, cursor: k.link ? 'pointer' : 'default' }" @click="k.link && emit('navigate', k.link)">
          <div class="kpi-top">
            <span class="kpi-label">{{ k.label }}</span>
            <el-icon :style="{ color: k.color, fontSize: '24px' }"><component :is="k.icon" /></el-icon>
          </div>
          <div class="kpi-value" :style="{ color: k.color }">{{ k.value }}</div>
          <div class="kpi-sub">
            <span v-if="k.pct !== null && k.pct !== undefined">
              今日
              <span :class="k.pct >= 0 ? 'up' : 'down'">
                {{ k.pct >= 0 ? '▲' : '▼' }} {{ Math.abs(k.pct) }}%
              </span>
              vs 昨日
            </span>
            <span v-else style="color:#aaa;">{{ k.subText }}</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 趋势图 -->
    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="chart-header">
          <span class="chart-title">📈 近 7 天交易趋势</span>
          <el-radio-group v-model="trendMode" size="small" @change="renderTrend">
            <el-radio-button value="sales">销售额</el-radio-button>
            <el-radio-button value="orders">订单量</el-radio-button>
            <el-radio-button value="both">双轴对比</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="trendChartRef" style="height:300px;"></div>
    </el-card>

    <!-- 中层：分类销售 + 订单状态 -->
    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="14">
        <el-card shadow="never" style="height:320px;">
          <template #header><span class="chart-title">📦 各分类销售额排行</span></template>
          <div ref="barChartRef" style="height:240px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" style="height:320px;">
          <template #header><span class="chart-title">🗂 订单状态分布</span></template>
          <div ref="pieChartRef" style="height:240px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底层：热销榜 + 会员分布 + 低库存 -->
    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <div class="chart-header"><span class="chart-title">🏆 热销商品 Top 5</span><el-tag type="danger" size="small">实时</el-tag></div>
          </template>
          <div v-for="(item, idx) in stats.hot_data" :key="idx" class="hot-row" style="cursor:pointer;" @click="emit('navigate','goods')">
            <span class="hot-rank" :class="['r'+( idx+1)]">{{ idx + 1 }}</span>
            <img :src="item.img" class="hot-img" />
            <div class="hot-info">
              <div class="hot-title">{{ item.title }}</div>
              <div class="hot-meta">{{ item.count }} 单 · ¥{{ item.amount }}</div>
            </div>
            <el-progress :percentage="Math.round(item.count / (stats.hot_data[0]?.count||1) * 100)"
              :show-text="false" :stroke-width="6" style="width:80px;" />
          </div>
          <el-empty v-if="!stats.hot_data?.length" description="暂无订单数据" :image-size="60" />
        </el-card>
      </el-col>

      <el-col :span="7">
        <el-card shadow="never">
          <template #header><span class="chart-title">👥 会员等级分布</span></template>
          <div ref="levelChartRef" style="height:220px;"></div>
        </el-card>
      </el-col>

      <el-col :span="7">
        <el-card shadow="never">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">⚠️ 低库存预警</span>
              <el-tag type="warning" size="small">库存 &lt; 10</el-tag>
            </div>
          </template>
          <div v-if="!stats.low_stock?.length" style="text-align:center;color:#aaa;padding:40px 0;">库存充足，无预警</div>
          <div v-for="item in stats.low_stock" :key="item.id" class="stock-row" style="cursor:pointer;" @click="emit('navigate','goods')">
            <img :src="item.img" class="hot-img" />
            <div class="hot-info">
              <div class="hot-title">{{ item.title }}</div>
              <el-tag :type="item.stock === 0 ? 'danger' : 'warning'" size="small">库存 {{ item.stock }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { Money, List, User, Goods, StarFilled, Van } from '@element-plus/icons-vue'

const emit = defineEmits(['navigate'])

const stats = ref({})
const trendMode = ref('both')
const trendChartRef = ref(null)
const barChartRef = ref(null)
const pieChartRef = ref(null)
const levelChartRef = ref(null)

const kpiCards = computed(() => {
  const s = stats.value
  if (!s.total_orders && s.total_orders !== 0) return []
  return [
    { label: '累计销售额 (GMV)', value: `¥ ${s.total_sales?.toFixed(2) ?? '0.00'}`, color: '#6366f1', icon: 'Money', pct: s.sales_pct, subText: '', link: 'orders' },
    { label: '今日订单量', value: `${s.today_orders ?? 0} 单`, color: '#0ea5e9', icon: 'List', pct: s.orders_pct, subText: '', link: 'orders' },
    { label: '客单价 (AOV)', value: `¥ ${s.aov ?? '0.00'}`, color: '#f59e0b', icon: 'Money', pct: null, subText: `待发货 ${s.pending_ship ?? 0} 单`, link: 'orders' },
    { label: '注册会员数', value: `${s.total_members ?? 0} 人`, color: '#10b981', icon: 'User', pct: null, subText: `评价均分 ${s.avg_rating ?? 0} ⭐`, link: 'members' },
  ]
})

const renderTrend = () => {
  const s = stats.value
  if (!s.trend_dates || !trendChartRef.value) return
  const chart = echarts.getInstanceByDom(trendChartRef.value) || echarts.init(trendChartRef.value)
  const series = []
  const yAxis = []
  if (trendMode.value === 'sales' || trendMode.value === 'both') {
    yAxis.push({ type: 'value', name: '销售额(¥)', position: 'left', axisLabel: { formatter: v => `¥${v}` } })
    series.push({ name: '销售额', type: 'line', smooth: true, yAxisIndex: 0,
      areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(99,102,241,0.3)'},{offset:1,color:'rgba(99,102,241,0)'}]) },
      data: s.trend_sales, itemStyle: { color: '#6366f1' }, lineStyle: { width: 3 } })
  }
  if (trendMode.value === 'orders' || trendMode.value === 'both') {
    yAxis.push({ type: 'value', name: '订单量', position: trendMode.value === 'both' ? 'right' : 'left' })
    series.push({ name: '订单量', type: 'bar', yAxisIndex: trendMode.value === 'both' ? 1 : 0,
      data: s.trend_orders, itemStyle: { color: '#0ea5e9', borderRadius: [4,4,0,0] }, barMaxWidth: 40 })
  }
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { top: 0 },
    grid: { left: 60, right: 60, bottom: 30, top: 40 },
    xAxis: { type: 'category', data: s.trend_dates, axisLine: { lineStyle: { color: '#eee' } } },
    yAxis,
    series
  }, true)
}

const renderBar = () => {
  const s = stats.value
  if (!s.category_data?.length || !barChartRef.value) return
  const chart = echarts.getInstanceByDom(barChartRef.value) || echarts.init(barChartRef.value)
  const sorted = [...s.category_data].sort((a, b) => a.sales - b.sales)
  chart.off('click')
  chart.on('click', () => emit('navigate', 'goods'))
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: p => `${p[0].name}<br/>销售额：¥${p[0].value}` },
    grid: { left: 80, right: 20, top: 10, bottom: 20 },
    xAxis: { type: 'value', axisLabel: { formatter: v => `¥${v}` } },
    yAxis: { type: 'category', data: sorted.map(d => d.name) },
    series: [{ type: 'bar', data: sorted.map(d => d.sales), barMaxWidth: 22,
      itemStyle: { borderRadius: [0,4,4,0],
        color: new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#6366f1'},{offset:1,color:'#a5b4fc'}]) },
      label: { show: true, position: 'right', formatter: p => `¥${p.value}` } }]
  })
}

const renderPie = () => {
  const s = stats.value
  if (!s.status_data?.length || !pieChartRef.value) return
  const chart = echarts.getInstanceByDom(pieChartRef.value) || echarts.init(pieChartRef.value)
  const colors = { '待发货': '#f59e0b', '运输中': '#0ea5e9', '待评价': '#8b5cf6', '已完成': '#10b981', '已取消': '#ef4444', '拼团中': '#f97316' }
  chart.off('click')
  chart.on('click', () => emit('navigate', 'orders'))
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 单 ({d}%)' },
    legend: { bottom: 0, left: 'center', itemWidth: 10, itemHeight: 10 },
    series: [{ type: 'pie', radius: ['45%', '72%'], center: ['50%', '45%'],
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: s.status_data.map(d => ({ ...d, itemStyle: { color: colors[d.name] } })) }]
  })
}

const renderLevel = () => {
  const s = stats.value
  if (!s.level_data?.length || !levelChartRef.value) return
  const chart = echarts.getInstanceByDom(levelChartRef.value) || echarts.init(levelChartRef.value)
  const colors = { '普通会员': '#94a3b8', '黄金VIP': '#f59e0b', '钻石VIP': '#6366f1' }
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 人 ({d}%)' },
    legend: { bottom: 0, left: 'center', itemWidth: 10, itemHeight: 10 },
    series: [{ type: 'pie', radius: ['40%', '68%'], center: ['50%', '43%'],
      itemStyle: { borderRadius: 5, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
      data: s.level_data.map(d => ({ ...d, itemStyle: { color: colors[d.name] ?? '#ccc' } })) }]
  })
}

onMounted(async () => {
  const res = await axios.get('http://localhost:5000/api/admin/stats')
  if (res.data.code === 200) {
    stats.value = res.data.data
    await nextTick()
    renderTrend()
    renderBar()
    renderPie()
    renderLevel()
  }
})
</script>

<style scoped>
.dashboard { padding-bottom: 20px; }
.kpi-row { margin-bottom: 16px; }
.kpi-card { background: #fff; border-radius: 10px; padding: 18px 20px; box-shadow: 0 1px 8px rgba(0,0,0,0.07); transition: box-shadow .2s; }
.kpi-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.12); }
.kpi-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.kpi-label { font-size: 13px; color: #888; }
.kpi-value { font-size: 26px; font-weight: 700; margin-bottom: 6px; }
.kpi-sub { font-size: 12px; color: #999; }
.up { color: #ef4444; font-weight: 600; }
.down { color: #10b981; font-weight: 600; }
.chart-card { margin-bottom: 0; }
.chart-header { display: flex; justify-content: space-between; align-items: center; }
.chart-title { font-size: 14px; font-weight: 600; color: #333; }
.hot-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.hot-row:last-child { border-bottom: none; }
.hot-rank { width: 22px; height: 22px; border-radius: 50%; background: #f0f2f5; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.r1 { background: #ef4444; color: #fff; }
.r2 { background: #f97316; color: #fff; }
.r3 { background: #f59e0b; color: #fff; }
.hot-img { width: 38px; height: 38px; border-radius: 6px; object-fit: cover; flex-shrink: 0; }
.hot-info { flex: 1; min-width: 0; }
.hot-title { font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hot-meta { font-size: 12px; color: #999; margin-top: 2px; }
.stock-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.stock-row:last-child { border-bottom: none; }
</style>
