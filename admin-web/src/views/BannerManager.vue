<template>
  <div class="banner-manager">
    <el-card>
      <template #header><div style="display: flex; justify-content: space-between;"><span>🖼️ 轮播图列表</span><el-button type="primary" :icon="Plus" @click="openAddBannerDialog">添加轮播图</el-button></div></template>
      <el-table :data="bannerList" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="图片"><template #default="scope"><img :src="scope.row.img" alt="轮播图" style="width: 200px; height: 80px; object-fit: cover; border-radius: 4px;"></template></el-table-column>
        <el-table-column prop="note" label="备注" />
        <el-table-column label="操作" width="120"><template #default="scope"><el-button size="small" type="danger" :icon="Delete" @click="deleteBanner(scope.row)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showBannerDialog" title="添加轮播图" width="500px">
      <el-form label-width="80px">
        <el-form-item label="图片">
          <el-upload class="avatar-uploader" action="http://localhost:5000/api/upload" :show-file-list="false" :on-success="handleBannerUploadSuccess" name="file">
            <img v-if="bannerForm.img" :src="bannerForm.img" alt="预览图" style="width:100%;height:150px;object-fit:cover;" />
            <el-icon v-else class="avatar-uploader-icon" style="width:100%"><Plus /></el-icon>
          </el-upload>
          <div style="margin-top:10px;"><el-button type="success" size="small" @click="setRandomBanner">🎲 一键生成测试图</el-button></div>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="bannerForm.note" placeholder="例如: 618大促" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showBannerDialog = false">取消</el-button><el-button type="primary" @click="submitBanner">确认添加</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'

const bannerList = ref([])
const showBannerDialog = ref(false)
const bannerForm = reactive({ img: '', note: '' })

const loadBanners = async () => {
    try {
        const res = await axios.get('http://localhost:5000/api/banners');
        bannerList.value = res.data.data
    } catch (e) {
        ElMessage.error('获取轮播图失败')
    }
}

const openAddBannerDialog = () => { bannerForm.img = ''; bannerForm.note = ''; showBannerDialog.value = true }

const handleBannerUploadSuccess = (res) => {
    if(res.code===200) bannerForm.img = res.url
    else ElMessage.error('上传失败')
}

const setRandomBanner = () => { bannerForm.img = `https://picsum.photos/800/400?random=${Math.random()}` }

const submitBanner = async () => {
    if(!bannerForm.img) return ElMessage.warning('请上传图片');
    try {
        await axios.post('http://localhost:5000/api/banners', bannerForm);
        ElMessage.success('添加成功');
        showBannerDialog.value=false;
        loadBanners()
    } catch (e) {
        ElMessage.error('操作失败')
    }
}

const deleteBanner = (row) => {
    ElMessageBox.confirm('确定删除?').then(async()=>{
        try {
            await axios.delete(`http://localhost:5000/api/banners/${row.id}`);
            loadBanners()
            ElMessage.success('删除成功')
        } catch(e) {
            ElMessage.error('删除失败')
        }
    }).catch(() => {})
}

onMounted(() => {
    loadBanners()
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
</style>
