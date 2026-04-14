<template>
  <div class="seckill-settings">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>秒杀规则设置</span>
        </div>
      </template>
      <el-form label-width="140px" class="settings-form">
        <el-form-item label="秒杀支付时限">
          <el-input-number v-model="systemConfig.seckill_time_limit" :min="1" :max="60" />
          <span class="form-tip">分钟，用户下单后需在该时间内完成支付。</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSystemConfig">保存秒杀规则</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>秒杀商品设置</span>
          <el-button @click="loadProducts">刷新</el-button>
        </div>
      </template>

      <el-alert
        title="这里维护商品级秒杀参数，和商品管理中的秒杀配置保持一致。"
        type="info"
        :closable="false"
        show-icon
        class="table-alert"
      />

      <el-table :data="seckillProducts" border stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="商品" min-width="260">
          <template #default="scope">
            <div class="product-cell">
              <img :src="scope.row.img" alt="商品图" class="product-thumb" />
              <div>
                <div class="product-title">{{ scope.row.title }}</div>
                <div class="product-category">{{ scope.row.category || '未分类' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="原价" width="110">
          <template #default="scope">
            <span class="price-text">¥{{ formatPrice(scope.row.price) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="秒杀价" width="110">
          <template #default="scope">
            <span class="price-text seckill">¥{{ formatPrice(scope.row.seckill_price ?? scope.row.price) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="秒杀库存" width="100">
          <template #default="scope">
            <el-tag :type="(scope.row.seckill_stock ?? 0) > 0 ? 'danger' : 'info'">
              {{ scope.row.seckill_stock ?? 0 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="限购" width="90">
          <template #default="scope">
            {{ scope.row.seckill_limit_per_user ?? 1 }} 件
          </template>
        </el-table-column>
        <el-table-column label="活动时间" min-width="280">
          <template #default="scope">
            <div class="time-text">{{ scope.row.seckill_start_at || '未设置开始时间' }}</div>
            <div class="time-text">{{ scope.row.seckill_end_at || '未设置结束时间' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row)">
              {{ getStatusText(scope.row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" plain @click="openEditDialog(scope.row)">编辑秒杀</el-button>
            <el-button size="small" type="warning" plain @click="disableSeckill(scope.row)">取消秒杀</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!seckillProducts.length" description="当前还没有配置秒杀商品" />
    </el-card>

    <el-dialog v-model="dialogVisible" title="编辑秒杀商品" width="520px">
      <el-form label-width="110px">
        <el-form-item label="商品名称">
          <el-input :model-value="editingProduct.title" disabled />
        </el-form-item>
        <el-form-item label="商品分类">
          <el-input :model-value="editingProduct.category" disabled />
        </el-form-item>
        <el-form-item label="商品原价">
          <el-input :model-value="`¥${formatPrice(editingProduct.price)}`" disabled />
        </el-form-item>
        <el-form-item label="秒杀价">
          <el-input-number v-model="editingProduct.seckill_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="秒杀库存">
          <el-input-number v-model="editingProduct.seckill_stock" :min="0" :step="1" />
        </el-form-item>
        <el-form-item label="每人限购">
          <el-input-number v-model="editingProduct.seckill_limit_per_user" :min="1" :step="1" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="editingProduct.seckill_start_at"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择开始时间"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="editingProduct.seckill_end_at"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择结束时间"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProductSeckill">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const systemConfig = reactive({
  group_buy_people: 2,
  seckill_time_limit: 5,
  group_buy_discount: 0.8
})

const productList = ref([])
const dialogVisible = ref(false)
const editingProduct = reactive({
  id: 0,
  title: '',
  category: '',
  price: 0,
  img: '',
  stock: 0,
  description: '',
  is_on_sale: true,
  seckill_price: 0,
  seckill_stock: 0,
  seckill_limit_per_user: 1,
  seckill_start_at: '',
  seckill_end_at: ''
})

const seckillProducts = computed(() => productList.value.filter(item => item.is_seckill || (item.category || '').includes('秒杀')))

const formatPrice = (value) => Number(value || 0).toFixed(2)

const getStatusText = (row) => {
  const now = Date.now()
  const start = row.seckill_start_at ? new Date(row.seckill_start_at.replace(' ', 'T')).getTime() : null
  const end = row.seckill_end_at ? new Date(row.seckill_end_at.replace(' ', 'T')).getTime() : null
  const stock = Number(row.seckill_stock ?? 0)
  if (stock <= 0) return '已售罄'
  if (start && now < start) return '未开始'
  if (end && now > end) return '已结束'
  return '进行中'
}

const getStatusType = (row) => {
  const text = getStatusText(row)
  if (text === '进行中') return 'danger'
  if (text === '未开始') return 'warning'
  return 'info'
}

const loadConfig = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/common/config')
    if (res.data.code === 200) {
      systemConfig.group_buy_people = parseInt(res.data.data.group_buy_people, 10)
      systemConfig.seckill_time_limit = parseInt(res.data.data.seckill_time_limit, 10)
      systemConfig.group_buy_discount = parseFloat(res.data.data.group_buy_discount)
    }
  } catch (error) {
    ElMessage.error('加载配置失败')
  }
}

const saveSystemConfig = async () => {
  try {
    await axios.post('http://localhost:5000/api/admin/config', systemConfig)
    ElMessage.success('秒杀规则已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const loadProducts = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/products')
    productList.value = res.data.data || []
  } catch (error) {
    ElMessage.error('加载秒杀商品失败')
  }
}

const openEditDialog = (row) => {
  Object.assign(editingProduct, {
    id: row.id,
    title: row.title,
    category: row.category || '',
    price: Number(row.price || 0),
    img: row.img || '',
    stock: Number(row.stock || 0),
    description: row.description || '',
    is_on_sale: row.is_on_sale,
    seckill_price: row.seckill_price ?? row.price ?? 0,
    seckill_stock: row.seckill_stock ?? row.stock ?? 0,
    seckill_limit_per_user: row.seckill_limit_per_user ?? 1,
    seckill_start_at: row.seckill_start_at || '',
    seckill_end_at: row.seckill_end_at || ''
  })
  dialogVisible.value = true
}

const saveProductSeckill = async () => {
  if (!editingProduct.seckill_start_at || !editingProduct.seckill_end_at) {
    return ElMessage.warning('请先设置完整的秒杀时间')
  }
  if (new Date(editingProduct.seckill_end_at) <= new Date(editingProduct.seckill_start_at)) {
    return ElMessage.warning('结束时间必须晚于开始时间')
  }

  try {
    await axios.put(`http://localhost:5000/api/products/${editingProduct.id}`, {
      title: editingProduct.title,
      price: Number(editingProduct.price),
      img: editingProduct.img,
      category: editingProduct.category,
      description: editingProduct.description,
      stock: Number(editingProduct.stock),
      is_on_sale: editingProduct.is_on_sale,
      is_seckill: true,
      seckill_price: Number(editingProduct.seckill_price),
      seckill_stock: Number(editingProduct.seckill_stock),
      seckill_limit_per_user: Number(editingProduct.seckill_limit_per_user),
      seckill_start_at: editingProduct.seckill_start_at,
      seckill_end_at: editingProduct.seckill_end_at
    })
    dialogVisible.value = false
    await loadProducts()
    ElMessage.success('秒杀商品已更新')
  } catch (error) {
    ElMessage.error('保存秒杀商品失败')
  }
}

const disableSeckill = async (row) => {
  try {
    await ElMessageBox.confirm(`确认取消「${row.title}」的秒杀设置吗？`, '取消秒杀', {
      type: 'warning'
    })
    const categoryList = (row.category || '')
      .split(',')
      .map(item => item.trim())
      .filter(item => item && item !== '秒杀')
      .join(',')
    await axios.put(`http://localhost:5000/api/products/${row.id}`, {
      title: row.title,
      price: Number(row.price),
      img: row.img,
      category: categoryList,
      description: row.description || '',
      stock: Number(row.stock ?? 0),
      is_on_sale: row.is_on_sale,
      is_seckill: false,
      seckill_price: null,
      seckill_stock: 0,
      seckill_limit_per_user: 1,
      seckill_start_at: '',
      seckill_end_at: ''
    })
    await loadProducts()
    ElMessage.success('已取消秒杀')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消秒杀失败')
    }
  }
}

onMounted(() => {
  loadConfig()
  loadProducts()
})
</script>

<style scoped>
.seckill-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.settings-card {
  border-radius: 18px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-weight: 700;
}

.settings-form {
  max-width: 640px;
  margin-top: 12px;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 13px;
}

.table-alert {
  margin-bottom: 16px;
}

.product-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-thumb {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  object-fit: cover;
  background: #f5f7fa;
}

.product-title {
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
}

.product-category,
.time-text {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.price-text {
  font-weight: 700;
  color: #303133;
}

.price-text.seckill {
  color: #f56c6c;
}
</style>
