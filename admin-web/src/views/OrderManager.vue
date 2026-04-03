<template>
  <div class="order-manager">
    <el-card>
      <template #header>
        <div class="toolbar">
          <span>订单处理中心</span>
          <div class="toolbar-actions">
            <el-button type="success" plain :icon="Download" @click="exportExcel">导出 Excel</el-button>
            <el-button type="primary" plain :icon="Refresh" @click="loadOrders">刷新列表</el-button>
          </div>
        </div>
      </template>

      <el-table :data="orderList" border stripe empty-text="暂无订单">
        <el-table-column prop="no" label="订单号" width="180" />
        <el-table-column prop="date" label="时间" width="170" />
        <el-table-column label="商品" min-width="220">
          <template #default="scope">
            <div class="product-cell">
              <img :src="scope.row.img" alt="" class="product-img" />
              <span>{{ scope.row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="user" label="买家" width="120" />
        <el-table-column label="金额" width="100">
          <template #default="scope">
            <b>￥{{ scope.row.amount }}</b>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 1" type="danger">待发货</el-tag>
            <el-tag v-else-if="scope.row.status === 2" type="warning">运输中</el-tag>
            <el-tag v-else-if="scope.row.status === 3" type="info">待评价</el-tag>
            <el-tag v-else type="success">已完成</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tracking_no" label="快递单号" width="180" />
        <el-table-column label="操作" width="140">
          <template #default="scope">
            <el-button v-if="scope.row.status === 1" type="primary" size="small" @click="shipOrder(scope.row)">
              发货
            </el-button>
            <span v-else class="muted-action">无操作</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Refresh } from '@element-plus/icons-vue'

const orderList = ref([])

const loadOrders = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/admin/orders')
    orderList.value = res.data?.data || []
  } catch (error) {
    ElMessage.error('获取订单失败')
  }
}

const shipOrder = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入快递单号', '订单发货', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '快递单号不能为空'
    })

    await axios.post(`http://localhost:5000/api/admin/orders/${row.id}/ship`, {
      tracking_no: value
    })
    ElMessage.success('发货成功')
    await loadOrders()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error?.response?.data?.msg || '操作失败')
  }
}

const exportExcel = () => {
  if (!orderList.value.length) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  let csvContent = 'data:text/csv;charset=utf-8,\uFEFF'
  csvContent += '订单号,商品名称,买家,金额,状态,快递单号,下单时间\n'

  orderList.value.forEach((row) => {
    const statusText =
      row.status === 1 ? '待发货' :
      row.status === 2 ? '运输中' :
      row.status === 3 ? '待评价' : '已完成'

    csvContent += `${row.no},${row.title},${row.user},${row.amount},${statusText},${row.tracking_no || ''},${row.date}\n`
  })

  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `订单报表_${Date.now()}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('报表导出成功')
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.product-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-img {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  object-fit: cover;
}

.muted-action {
  color: #999;
  font-size: 12px;
}
</style>
