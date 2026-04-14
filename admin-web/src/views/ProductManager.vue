<template>
  <div class="product-manager">
    <el-card class="manager-card">
      <template #header>
        <div class="card-header">
          <span>商品列表</span>
          <el-button type="primary" :icon="Plus" @click="openAddDialog">发布新商品</el-button>
        </div>
      </template>

      <el-table :data="productList" border stripe class="product-table">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="图片" width="88">
          <template #default="scope">
            <img :src="scope.row.img" alt="商品图片" class="table-thumb" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="商品名称" min-width="180" />
        <el-table-column prop="category" label="分类" width="220">
          <template #default="scope">
            <el-tag
              v-for="tag in splitCategory(scope.row.category)"
              :key="tag"
              type="info"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="原价" width="120">
          <template #default="scope">
            <span class="price-text">¥{{ formatPrice(scope.row.price) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="90">
          <template #default="scope">
            <el-tag :type="getStockTag(scope.row.stock)">
              {{ scope.row.stock }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="拼团" width="170">
          <template #default="scope">
            <div v-if="isGroupProduct(scope.row)" class="mode-cell">
              <div class="mode-price group">¥{{ formatPrice(getGroupPrice(scope.row.price)) }}</div>
              <div class="mode-sub">{{ systemConfig.group_buy_people }} 人成团 · {{ Math.round(systemConfig.group_buy_discount * 100) }}% 折扣</div>
            </div>
            <span v-else class="mode-empty">-</span>
          </template>
        </el-table-column>
        <el-table-column label="秒杀" width="190">
          <template #default="scope">
            <div v-if="scope.row.is_seckill" class="mode-cell">
              <div class="mode-price seckill">¥{{ formatPrice(scope.row.seckill_price ?? scope.row.price) }}</div>
              <div class="mode-sub">库存 {{ scope.row.seckill_stock ?? 0 }} · 限购 {{ scope.row.seckill_limit_per_user ?? 1 }} 件</div>
            </div>
            <span v-else class="mode-empty">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_on_sale ? 'success' : 'info'">
              {{ scope.row.is_on_sale ? '上架中' : '已下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" plain @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button
              size="small"
              :type="scope.row.is_on_sale ? 'warning' : 'success'"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.is_on_sale ? '下架' : '上架' }}
            </el-button>
            <el-button size="small" type="danger" :icon="Delete" circle @click="deleteProduct(scope.row)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEditMode ? '编辑商品' : '发布新商品'" width="560px">
      <el-form label-width="90px">
        <el-form-item label="名称">
          <el-input v-model="form.title" placeholder="例如：iPhone 16" />
        </el-form-item>
        <el-form-item label="分类">
          <el-checkbox-group v-model="form.category">
            <el-checkbox label="手机" value="手机" />
            <el-checkbox label="电脑" value="电脑" />
            <el-checkbox label="数码" value="数码" />
            <el-checkbox label="热卖" value="热卖" />
            <el-checkbox label="拼团" value="拼团" />
            <el-checkbox label="秒杀" value="秒杀" />
            <el-checkbox label="平板" value="平板" />
            <el-checkbox label="相机" value="相机" />
            <el-checkbox label="耳机" value="耳机" />
            <el-checkbox label="手表" value="手表" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="form.stock" :min="0" :step="10" />
        </el-form-item>
        <el-form-item label="商品简介">
          <el-input v-model="form.description" type="textarea" rows="3" placeholder="请输入商品详细介绍..." />
        </el-form-item>

        <template v-if="form.category.includes('拼团')">
          <el-divider content-position="left">拼团预览</el-divider>
          <div class="mode-preview group-preview">
            <div class="preview-head">
              <span>当前采用全局拼团规则</span>
              <el-tag type="primary" effect="plain">{{ systemConfig.group_buy_people }} 人团</el-tag>
            </div>
            <div class="preview-copy">
              预计拼团价 <b>¥{{ formatPrice(getGroupPrice(form.price)) }}</b>
              <span>折扣 {{ Math.round(systemConfig.group_buy_discount * 100) }}%</span>
            </div>
          </div>
        </template>

        <template v-if="form.category.includes('秒杀')">
          <el-divider content-position="left">秒杀参数</el-divider>
          <el-form-item label="秒杀价">
            <el-input-number v-model="form.seckill_price" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="秒杀库存">
            <el-input-number v-model="form.seckill_stock" :min="0" :step="1" />
          </el-form-item>
          <el-form-item label="限购">
            <el-input-number v-model="form.seckill_limit_per_user" :min="1" :step="1" />
          </el-form-item>
          <el-form-item label="开始时间">
            <el-date-picker
              v-model="form.seckill_start_at"
              type="datetime"
              value-format="YYYY-MM-DD HH:mm:ss"
              placeholder="选择开始时间"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="结束时间">
            <el-date-picker
              v-model="form.seckill_end_at"
              type="datetime"
              value-format="YYYY-MM-DD HH:mm:ss"
              placeholder="选择结束时间"
              style="width: 100%;"
            />
          </el-form-item>
        </template>

        <el-form-item label="图片">
          <el-upload
            class="avatar-uploader"
            action="http://localhost:5000/api/upload"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            name="file"
          >
            <img v-if="form.img" :src="form.img" class="avatar" alt="预览图" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="image-action-row">
            <el-button type="success" size="small" @click="setRandomProductImage">一键生成测试图</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'

const productList = ref([])
const dialogVisible = ref(false)
const isEditMode = ref(false)
const systemConfig = reactive({
  group_buy_people: 2,
  group_buy_discount: 0.8
})

const form = reactive({
  id: 0,
  title: '',
  price: 99,
  img: '',
  category: [],
  description: '',
  stock: 999,
  seckill_price: null,
  seckill_stock: 0,
  seckill_limit_per_user: 1,
  seckill_start_at: '',
  seckill_end_at: ''
})

const splitCategory = (categoryText) => (categoryText ? categoryText.split(',').filter(Boolean) : [])
const isGroupProduct = (row) => splitCategory(row.category).includes('拼团')
const formatPrice = (value) => Number(value || 0).toFixed(2)
const getGroupPrice = (price) => Number(price || 0) * Number(systemConfig.group_buy_discount || 1)

const getStockTag = (stock) => {
  const value = Number(stock || 0)
  if (value > 10) return 'success'
  if (value > 0) return 'warning'
  return 'danger'
}

const loadProducts = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/products')
    productList.value = res.data.data || []
  } catch (error) {
    ElMessage.error('加载商品失败')
  }
}

const loadConfig = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/common/config')
    if (res.data.code === 200) {
      systemConfig.group_buy_people = parseInt(res.data.data.group_buy_people, 10)
      systemConfig.group_buy_discount = parseFloat(res.data.data.group_buy_discount)
    }
  } catch (error) {
    ElMessage.error('加载活动配置失败')
  }
}

const resetForm = () => {
  form.id = 0
  form.title = ''
  form.price = 99
  form.img = ''
  form.category = []
  form.description = ''
  form.stock = 999
  form.seckill_price = null
  form.seckill_stock = 0
  form.seckill_limit_per_user = 1
  form.seckill_start_at = ''
  form.seckill_end_at = ''
}

const openAddDialog = () => {
  isEditMode.value = false
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEditMode.value = true
  form.id = row.id
  form.title = row.title || ''
  form.price = Number(row.price || 0)
  form.img = row.img || ''
  form.category = splitCategory(row.category)
  form.description = row.description || ''
  form.stock = row.stock ?? 999
  form.seckill_price = row.seckill_price ?? null
  form.seckill_stock = row.seckill_stock ?? 0
  form.seckill_limit_per_user = row.seckill_limit_per_user ?? 1
  form.seckill_start_at = row.seckill_start_at || ''
  form.seckill_end_at = row.seckill_end_at || ''
  dialogVisible.value = true
}

const setRandomProductImage = () => {
  form.img = `https://picsum.photos/400/400?random=${Math.random()}`
}

const handleUploadSuccess = (res) => {
  if (res.code === 200) {
    form.img = res.url
    return
  }
  ElMessage.error('上传失败')
}

const handleUploadError = () => {
  ElMessage.error('上传出错')
}

const submitForm = async () => {
  if (!form.title) return ElMessage.warning('请输入名称')
  if (form.category.length === 0) return ElMessage.warning('请至少选择一个分类')

  const submitData = {
    ...form,
    price: Number(form.price),
    stock: Number(form.stock),
    category: form.category.join(','),
    description: form.description,
    is_seckill: form.category.includes('秒杀'),
    seckill_price: form.seckill_price === null ? null : Number(form.seckill_price),
    seckill_stock: Number(form.seckill_stock),
    seckill_limit_per_user: Number(form.seckill_limit_per_user)
  }

  try {
    if (isEditMode.value) {
      await axios.put(`http://localhost:5000/api/products/${form.id}`, submitData)
    } else {
      await axios.post('http://localhost:5000/api/products', submitData)
    }
    dialogVisible.value = false
    await loadProducts()
    ElMessage.success('操作成功')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const toggleStatus = async (row) => {
  try {
    await axios.post(`http://localhost:5000/api/products/${row.id}/status`)
    await loadProducts()
    ElMessage.success(row.is_on_sale ? '已下架' : '已上架')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteProduct = (row) => {
  ElMessageBox.confirm(`确定删除「${row.title}」吗？`, '删除商品', {
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`http://localhost:5000/api/products/${row.id}`)
      await loadProducts()
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadConfig()
  loadProducts()
})
</script>

<style scoped>
.manager-card {
  border-radius: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-weight: 700;
}

.product-table :deep(.thumb-column .cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 12px;
  padding-bottom: 12px;
}

.thumb-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  overflow: hidden;
  border-radius: 14px;
  background: #f5f7fa;
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.05);
}

.table-thumb {
  display: block;
  width: 64px;
  height: 64px;
  min-width: 64px;
  max-width: 64px;
  min-height: 64px;
  max-height: 64px;
  object-fit: cover;
  aspect-ratio: 1 / 1;
}

.tag-item {
  margin-right: 4px;
  margin-bottom: 4px;
}

.price-text {
  color: #f56c6c;
  font-weight: 700;
}

.mode-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mode-price {
  font-weight: 700;
}

.mode-price.group {
  color: #1989fa;
}

.mode-price.seckill {
  color: #f56c6c;
}

.mode-sub,
.mode-empty {
  font-size: 12px;
  color: #909399;
}

.mode-preview {
  margin-bottom: 18px;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid rgba(64, 158, 255, 0.12);
  background: linear-gradient(135deg, rgba(236, 245, 255, 0.88), rgba(247, 251, 255, 0.96));
}

.preview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-weight: 700;
  color: #303133;
}

.preview-copy {
  margin-top: 10px;
  color: #606266;
}

.preview-copy b {
  color: #1989fa;
  margin: 0 6px;
}

.preview-copy span {
  margin-left: 8px;
}

.avatar-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 10px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar {
  width: 178px;
  height: 178px;
  object-fit: cover;
}

.image-action-row {
  margin-top: 8px;
}
</style>
