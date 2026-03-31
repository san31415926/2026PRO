<template>
  <div class="order-manager">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between;">
          <span>📦 订单处理中心</span>
          <div>
            <el-button type="success" plain :icon="Download" @click="exportExcel">导出Excel</el-button>
            <el-button type="primary" plain :icon="Refresh" @click="loadOrders">刷新列表</el-button>
          </div>
        </div>
      </template>
      <el-table :data="orderList" border stripe empty-text="暂无订单">
        <el-table-column prop="no" label="订单号" width="180" />
        <el-table-column prop="date" label="时间" width="150" />
        <el-table-column label="商品" min-width="180"><template #default="scope"><div style="display:flex; align-items:center;"><img :src="scope.row.img" alt="商品图片" style="width:40px; height:40px; margin-right:8px; border-radius:4px;"><span>{{ scope.row.title }}</span></div></template></el-table-column>
        <el-table-column prop="user" label="买家" width="100" />
        <el-table-column prop="amount" label="金额" width="100"><template #default="scope"><b>¥{{ scope.row.amount }}</b></template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="scope"><el-tag v-if="scope.row.status===1" type="danger">待发货</el-tag><el-tag v-else-if="scope.row.status===2" type="warning">已发货</el-tag><el-tag v-else type="success">已完成</el-tag></template></el-table-column>
        <el-table-column label="操作" width="120"><template #default="scope"><el-button v-if="scope.row.status===1" type="primary" size="small" @click="shipOrder(scope.row)">🚀 发货</el-button><span v-else style="color:#ccc; font-size:12px;">无操作</span></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Download, Refresh } from '@element-plus/icons-vue'

const orderList = ref([])

const loadOrders = async () => {
    try {
        const res = await axios.get('http://localhost:5000/api/admin/orders');
        orderList.value = res.data.data
    } catch(e) { ElMessage.error('获取订单失败') }
}

const shipOrder = async (row) => {
    try {
        await axios.post(`http://localhost:5000/api/admin/orders/${row.id}/ship`);
        ElMessage.success('发货成功')
        loadOrders()
    } catch (e) { ElMessage.error('操作失败') }
}

const exportExcel = () => {
    if (orderList.value.length === 0) return ElMessage.warning('暂无数据可导出');
    let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
    csvContent += "订单号,商品名称,买家,金额,状态,下单时间\n";
    orderList.value.forEach(row => {
        let statusStr = row.status === 1 ? '待发货' : (row.status === 2 ? '已发货' : '已完成');
        let dataString = `${row.no},${row.title},${row.user},${row.amount},${statusStr},${row.date}`;
        csvContent += dataString + "\n";
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `订单报表_${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    ElMessage.success('报表导出成功！');
}

onMounted(() => {
    loadOrders()
})
</script>
