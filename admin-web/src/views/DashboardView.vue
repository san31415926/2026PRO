<template>
  <div class="dashboard-container">
    <!-- 顶部 KPI 卡片 -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :span="6">
        <div class="kpi-card purple">
          <div class="card-icon"><el-icon><Money /></el-icon></div>
          <div class="card-info">
            <div class="label">总销售额 (GMV)</div>
            <div class="value">¥ {{ statsData.sales.toFixed(2) }}</div>
            <div class="trend">较昨日 <span class="up">+12.5% <el-icon><CaretTop /></el-icon></span></div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card blue">
          <div class="card-icon"><el-icon><List /></el-icon></div>
          <div class="card-info">
            <div class="label">总订单量</div>
            <div class="value">{{ statsData.orders }} 单</div>
            <div class="trend">较昨日 <span class="up">+5.2% <el-icon><CaretTop /></el-icon></span></div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card orange">
          <div class="card-icon"><el-icon><User /></el-icon></div>
          <div class="card-info">
            <div class="label">客单价 (AOV)</div>
            <div class="value">¥ {{ (statsData.sales / (statsData.orders || 1)).toFixed(2) }}</div>
            <div class="trend">较昨日 <span class="down">-2.1% <el-icon><CaretBottom /></el-icon></span></div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card green">
          <div class="card-icon"><el-icon><Goods /></el-icon></div>
          <div class="card-info">
            <div class="label">在售商品数</div>
            <div class="value">{{ statsData.products }} 件</div>
            <div class="trend">库存充足</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 中间：核心趋势图 -->
    <div class="chart-section">
        <div class="section-header">
            <h3>📈 近7天交易趋势</h3>
            <el-radio-group v-model="trendType" size="small">
                <el-radio-button label="sales">销售额</el-radio-button>
                <el-radio-button label="orders">订单量</el-radio-button>
            </el-radio-group>
        </div>
        <div id="main-trend-chart" style="width: 100%; height: 350px;"></div>
    </div>

    <!-- 底部：排行榜与占比 -->
    <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="14">
            <el-card shadow="hover" class="rank-card">
                <template #header>
                    <div class="card-header"><span>🏆 商品热销榜 Top 5</span><el-tag type="danger" size="small">实时</el-tag></div>
                </template>
                <el-table :data="hotProducts" style="width: 100%" :show-header="false">
                    <el-table-column type="index" width="50">
                        <template #default="scope">
                            <span :class="['rank-index', 'rank-'+(scope.$index+1)]">{{ scope.$index + 1 }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column width="60">
                        <template #default="scope"><img :src="scope.row.img" alt="商品图片" style="width:40px;height:40px;border-radius:4px;object-fit:cover;"></template>
                    </el-table-column>
                    <el-table-column prop="title" min-width="200" show-overflow-tooltip />
                    <el-table-column width="150" align="right">
                        <template #default="scope">
                            <div style="font-weight:bold;">{{ scope.row.count }} 件</div>
                            <div style="color:gray;font-size:12px;">¥ {{ scope.row.amount }}</div>
                        </template>
                    </el-table-column>
                </el-table>
            </el-card>
        </el-col>
        <el-col :span="10">
            <el-card shadow="hover">
                 <template #header><span>📊 订单状态分布</span></template>
                 <div id="pie-chart" style="width:100%;height:300px;"></div>
            </el-card>
        </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { Money, List, User, Goods, CaretTop, CaretBottom } from '@element-plus/icons-vue'

const statsData = ref({ sales: 0, orders: 0, products: 0 })
const hotProducts = ref([])
const trendType = ref('sales')

const loadStats = async () => {
    const res = await axios.get('http://localhost:5000/api/admin/stats');
    if (res.data.code === 200) {
        statsData.value = res.data.data;

        // 模拟热销数据 (基于真实订单统计)
        const orderRes = await axios.get('http://localhost:5000/api/admin/orders')
        if (orderRes.data.code === 200) {
            const orders = orderRes.data.data
            // 简单统计热销
            const productCounts = {}
            orders.forEach(o => {
                if(!productCounts[o.title]) productCounts[o.title] = { title: o.title, img: o.img, count: 0, amount: 0 }
                productCounts[o.title].count += 1
                productCounts[o.title].amount += o.amount
            })
            hotProducts.value = Object.values(productCounts).sort((a,b) => b.count - a.count).slice(0, 5)

            // 渲染订单状态饼图
            const statusCounts = { '待发货': 0, '已发货': 0, '已完成': 0 }
            orders.forEach(o => {
                if(o.status === 1 || o.status === 5) statusCounts['待发货']++
                else if(o.status === 2) statusCounts['已发货']++
                else statusCounts['已完成']++
            })
            const pieData = Object.keys(statusCounts).map(k => ({name: k, value: statusCounts[k]}))

            await nextTick();
            initDashboardCharts(res.data.data.chart, pieData)
        }
    }
}

const initDashboardCharts = (categoryData, pieData) => {
  // 1. 趋势图 (模拟数据)
  const lineDom = document.getElementById('main-trend-chart');
  if (lineDom) {
      echarts.getInstanceByDom(lineDom)?.dispose();
      const lineChart = echarts.init(lineDom);
      // 模拟近7天日期
      const dates = Array.from({length:7}, (_,i) => {
          const d = new Date(); d.setDate(d.getDate() - (6-i)); return `${d.getMonth()+1}-${d.getDate()}`
      })
      const mockSales = [1200, 1450, 1100, 1800, 2400, 2100, statsData.value.sales || 3000] // 模拟数据+真实总额

      lineChart.setOption({
          tooltip: { trigger: 'axis' },
          grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
          xAxis: { type: 'category', boundaryGap: false, data: dates },
          yAxis: { type: 'value' },
          series: [
            {
                name: '销售趋势',
                type: 'line',
                smooth: true,
                areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(64,158,255,0.3)'},{offset:1,color:'rgba(64,158,255,0)'}]) },
                data: mockSales,
                itemStyle: { color: '#409EFF' }
            }
          ]
      })
  }

  // 2. 饼图
  const pieDom = document.getElementById('pie-chart');
  if (pieDom) {
      echarts.getInstanceByDom(pieDom)?.dispose();
      const pieChart = echarts.init(pieDom);
      pieChart.setOption({
          tooltip: { trigger: 'item' },
          legend: { bottom: '5%', left: 'center' },
          series: [{
              name: '订单状态',
              type: 'pie',
              radius: ['40%', '70%'],
              avoidLabelOverlap: false,
              itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
              label: { show: false, position: 'center' },
              emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
              data: pieData
          }]
      })
  }
}

onMounted(() => {
    loadStats()
})
</script>

<style scoped>
/* Dashboard Styles */
.kpi-row { margin-bottom: 20px; }
.kpi-card { background: white; border-radius: 8px; padding: 20px; display: flex; align-items: center; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1); transition: transform 0.3s; }
.kpi-card:hover { transform: translateY(-5px); }
.kpi-card .card-icon { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; margin-right: 15px; color: white; }
.kpi-card.purple .card-icon { background: #8e44ad; }
.kpi-card.blue .card-icon { background: #2980b9; }
.kpi-card.orange .card-icon { background: #f39c12; }
.kpi-card.green .card-icon { background: #27ae60; }
.kpi-card .card-info .label { font-size: 14px; color: #999; margin-bottom: 5px; }
.kpi-card .card-info .value { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 5px; }
.kpi-card .card-info .trend { font-size: 12px; color: #666; }
.kpi-card .trend .up { color: #f56c6c; font-weight: bold; }
.kpi-card .trend .down { color: #67c23a; font-weight: bold; }

.chart-section { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.rank-index { display: inline-block; width: 20px; height: 20px; line-height: 20px; text-align: center; border-radius: 50%; background: #f0f2f5; font-size: 12px; font-weight: bold; }
.rank-1 { background: #f56c6c; color: white; }
.rank-2 { background: #e6a23c; color: white; }
.rank-3 { background: #409eff; color: white; }
</style>
