<template>
  <div class="product-manager">
    <el-card>
      <template #header><div style="display: flex; justify-content: space-between;"><span>🛍️ 商品列表</span><el-button type="primary" :icon="Plus" @click="openAddDialog">发布新商品</el-button></div></template>
      <el-table :data="productList" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="图片" width="80"><template #default="scope"><img :src="scope.row.img" alt="商品图片" style="width: 50px; height: 50px; border-radius: 4px; object-fit: cover;"></template></el-table-column>
        <el-table-column prop="title" label="商品名称" />
        <el-table-column prop="category" label="分类" width="180">
          <template #default="scope">
            <el-tag v-for="tag in (scope.row.category ? scope.row.category.split(',') : [])" :key="tag" type="info" style="margin-right:4px;margin-bottom:4px;">{{ tag }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="120"><template #default="scope"><span style="color:#f56c6c; font-weight:bold;">¥{{ scope.row.price }}</span></template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="scope"><el-tag :type="scope.row.is_on_sale ? 'success' : 'info'">{{ scope.row.is_on_sale ? '销售中' : '已下架' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="220"><template #default="scope"><el-button size="small" type="primary" plain @click="openEditDialog(scope.row)">编辑</el-button><el-button size="small" :type="scope.row.is_on_sale ? 'warning' : 'success'" @click="toggleStatus(scope.row)">{{ scope.row.is_on_sale ? '下架' : '上架' }}</el-button><el-button size="small" type="danger" :icon="Delete" circle @click="deleteProduct(scope.row)" /></template></el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEditMode ? '编辑商品' : '发布新商品'" width="500px">
      <el-form label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.title" placeholder="例如: iPhone 16" /></el-form-item>
        <el-form-item label="分类">
          <el-checkbox-group v-model="form.category">
            <el-checkbox label="手机" value="手机" /><el-checkbox label="电脑" value="电脑" /><el-checkbox label="数码" value="数码" /><el-checkbox label="热卖" value="热卖" />
            <el-checkbox label="拼团" value="拼团" /><el-checkbox label="秒杀" value="秒杀" /><el-checkbox label="平板" value="平板" /><el-checkbox label="相机" value="相机" />
            <el-checkbox label="耳机" value="耳机" /><el-checkbox label="手表" value="手表" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="商品简介"><el-input v-model="form.description" type="textarea" rows="3" placeholder="请输入商品详细介绍..." /></el-form-item>
        <el-form-item label="图片">
          <el-upload class="avatar-uploader" action="http://localhost:5000/api/upload" :show-file-list="false" :on-success="handleUploadSuccess" :on-error="handleUploadError" name="file">
            <img v-if="form.img" :src="form.img" class="avatar" alt="预览图" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div style="margin-top:5px;"><el-button type="success" size="small" @click="setRandomProductImage">🎲 一键生成测试图</el-button></div>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submitForm">确认</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'

const productList = ref([])
const dialogVisible = ref(false)
const isEditMode = ref(false)
const form = reactive({ id: 0, title: '', price: 99.0, img: '', category: [], description: '' })

const loadProducts = async () => {
    try {
        const res = await axios.get('http://localhost:5000/api/products');
        productList.value = res.data.data
    } catch(e) { ElMessage.error('加载商品失败') }
}

const openAddDialog = () => { isEditMode.value = false; form.title = ''; form.price = 99.0; form.img = ''; form.category = []; form.description = ''; dialogVisible.value = true }
const openEditDialog = (row) => { isEditMode.value = true; Object.assign(form, row); form.price = parseFloat(row.price); form.category = row.category ? row.category.split(',') : []; form.description = row.description || ''; dialogVisible.value = true }

const setRandomProductImage = () => { form.img = `https://picsum.photos/400/400?random=${Math.random()}` }
const handleUploadSuccess = (res) => { if (res.code === 200) form.img = res.url; else ElMessage.error('失败') }
const handleUploadError = () => ElMessage.error('出错')

const submitForm = async () => {
    if(!form.title) return ElMessage.warning('请输入名称');
    if(form.category.length === 0) return ElMessage.warning('请至少选择一个分类');
    const submitData = { ...form, price: Number(form.price), category: form.category.join(','), description: form.description };
    try {
        if(isEditMode.value) await axios.put(`http://localhost:5000/api/products/${form.id}`, submitData);
        else await axios.post('http://localhost:5000/api/products', submitData);
        dialogVisible.value=false;
        loadProducts();
        ElMessage.success('操作成功')
    } catch(e) { ElMessage.error('操作失败') }
}

const toggleStatus = async (row) => {
    try {
        await axios.post(`http://localhost:5000/api/products/${row.id}/status`);
        loadProducts()
        ElMessage.success(row.is_on_sale ? '已下架' : '已上架')
    } catch(e) { ElMessage.error('操作失败') }
}

const deleteProduct = (row) => {
    ElMessageBox.confirm('确定删除?').then(async()=>{
        try {
            await axios.delete(`http://localhost:5000/api/products/${row.id}`);
            loadProducts();
            ElMessage.success('删除成功')
        } catch(e) { ElMessage.error('删除失败') }
    }).catch(() => {})
}

onMounted(() => {
    loadProducts()
})
</script>

<style scoped>
.avatar-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}
.avatar-uploader :deep(.el-upload:hover) {
  border-color: #409EFF;
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
</style>
