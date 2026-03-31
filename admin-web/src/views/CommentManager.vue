<template>
  <div class="comment-manager">
    <el-card>
      <template #header><span>💬 用户评价管理</span></template>
      <el-table :data="commentList" border stripe empty-text="暂无评价">
        <el-table-column prop="date" label="时间" width="150" />
        <el-table-column prop="user" label="用户" width="120" />
        <el-table-column prop="product" label="商品" width="180" />
        <el-table-column prop="rating" label="评分" width="120"><template #default="scope"><el-rate v-model="scope.row.rating" disabled show-score text-color="#ff9900" /></template></el-table-column>
        <el-table-column prop="content" label="评价内容" />
        <el-table-column label="操作" width="100"><template #default="scope"><el-button size="small" type="danger" @click="deleteComment(scope.row)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const commentList = ref([])

const loadComments = async () => {
    try {
        const res = await axios.get('http://localhost:5000/api/admin/comments');
        commentList.value = res.data.data
    } catch(e) { ElMessage.error('加载评价失败') }
}

const deleteComment = (row) => {
    ElMessageBox.confirm('确定删除此评论?').then(async()=>{
        try {
            await axios.delete(`http://localhost:5000/api/admin/comments/${row.id}`);
            loadComments();
            ElMessage.success('删除成功')
        } catch(e) { ElMessage.error('删除失败') }
    }).catch(() => {})
}

onMounted(() => {
    loadComments()
})
</script>
