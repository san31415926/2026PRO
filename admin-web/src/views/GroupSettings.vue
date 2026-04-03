<template>
  <div class="group-settings">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>拼团规则设置</span>
        </div>
      </template>
      <el-form label-width="140px" class="settings-form">
        <el-form-item label="成团人数">
          <el-input-number v-model="systemConfig.group_buy_people" :min="2" :max="10" />
          <span class="form-tip">人，达到该人数后拼团成功。</span>
        </el-form-item>
        <el-form-item label="拼团折扣">
          <el-input-number v-model="systemConfig.group_buy_discount" :min="0.1" :max="0.95" :step="0.05" />
          <span class="form-tip">如 0.8 表示拼团价为原价的 8 折。</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSystemConfig">保存拼团规则</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>拼团商品设置</span>
          <el-button @click="loadProducts">刷新</el-button>
        </div>
      </template>

      <el-alert
        title="这里维护拼团商品列表，当前拼团价、成团人数和折扣来自上方全局拼团规则。"
        type="info"
        :closable="false"
        show-icon
        class="table-alert"
      />

      <el-table :data="groupProducts" border stripe>
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
        <el-table-column label="拼团价" width="110">
          <template #default="scope">
            <span class="price-text group">¥{{ formatPrice(getGroupPrice(scope.row.price)) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="成团人数" width="100">
          <template #default>
            {{ systemConfig.group_buy_people }} 人
          </template>
        </el-table-column>
        <el-table-column label="折扣" width="90">
          <template #default>
            {{ Math.round(systemConfig.group_buy_discount * 100) }}%
          </template>
        </el-table-column>
        <el-table-column label="库存" width="90">
          <template #default="scope">
            <el-tag :type="Number(scope.row.stock || 0) > 0 ? 'success' : 'info'">
              {{ scope.row.stock ?? 0 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="scope">
            <el-tag :type="scope.row.is_on_sale ? 'success' : 'info'">
              {{ scope.row.is_on_sale ? '上架中' : '已下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" plain @click="openEditDialog(scope.row)">编辑拼团</el-button>
            <el-button size="small" type="warning" plain @click="disableGroup(scope.row)">取消拼团</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!groupProducts.length" description="当前还没有配置拼团商品" />
    </el-card>

    <el-dialog v-model="dialogVisible" title="编辑拼团商品" width="520px">
      <el-form label-width="110px">
        <el-form-item label="商品名称">
          <el-input :model-value="editingProduct.title" disabled />
        </el-form-item>
        <el-form-item label="商品分类">
          <el-input :model-value="editingProduct.category" disabled />
        </el-form-item>
        <el-form-item label="商品原价">
          <el-input-number v-model="editingProduct.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="商品库存">
          <el-input-number v-model="editingProduct.stock" :min="0" :step="1" />
        </el-form-item>
        <el-form-item label="成团人数">
          <el-input :model-value="`${systemConfig.group_buy_people} 人`" disabled />
        </el-form-item>
        <el-form-item label="拼团折扣">
          <el-input :model-value="`${Math.round(systemConfig.group_buy_discount * 100)}%`" disabled />
        </el-form-item>
        <el-form-item label="预计拼团价">
          <el-input :model-value="`¥${formatPrice(getGroupPrice(editingProduct.price))}`" disabled />
        </el-form-item>
        <el-form-item label="上架状态">
          <el-switch
            v-model="editingProduct.is_on_sale"
            active-text="上架中"
            inactive-text="已下架"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveGroupProduct">保存</el-button>
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
  is_on_sale: true
})

const groupProducts = computed(() => productList.value.filter(item => (item.category || '').includes('拼团')))

const formatPrice = (value) => Number(value || 0).toFixed(2)
const getGroupPrice = (price) => Number(price || 0) * Number(systemConfig.group_buy_discount || 1)

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
    ElMessage.success('拼团规则已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const loadProducts = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/products')
    productList.value = res.data.data || []
  } catch (error) {
    ElMessage.error('加载拼团商品失败')
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
    is_on_sale: !!row.is_on_sale
  })
  dialogVisible.value = true
}

const saveGroupProduct = async () => {
  try {
    await axios.put(`http://localhost:5000/api/products/${editingProduct.id}`, {
      title: editingProduct.title,
      price: Number(editingProduct.price),
      img: editingProduct.img,
      category: editingProduct.category,
      description: editingProduct.description,
      stock: Number(editingProduct.stock),
      is_on_sale: editingProduct.is_on_sale
    })
    dialogVisible.value = false
    await loadProducts()
    ElMessage.success('拼团商品已更新')
  } catch (error) {
    ElMessage.error('保存拼团商品失败')
  }
}

const disableGroup = async (row) => {
  try {
    await ElMessageBox.confirm(`确认取消「${row.title}」的拼团设置吗？`, '取消拼团', {
      type: 'warning'
    })
    const categoryList = (row.category || '')
      .split(',')
      .map(item => item.trim())
      .filter(item => item && item !== '拼团')
      .join(',')
    await axios.put(`http://localhost:5000/api/products/${row.id}`, {
      title: row.title,
      price: Number(row.price),
      img: row.img,
      category: categoryList,
      description: row.description || '',
      stock: Number(row.stock ?? 0),
      is_on_sale: row.is_on_sale
    })
    await loadProducts()
    ElMessage.success('已取消拼团')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消拼团失败')
    }
  }
}

onMounted(() => {
  loadConfig()
  loadProducts()
})
</script>

<style scoped>
.group-settings {
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

.product-category {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.price-text {
  font-weight: 700;
  color: #303133;
}

.price-text.group {
  color: #1989fa;
}
</style>
