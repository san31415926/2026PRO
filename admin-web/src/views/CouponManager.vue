<template>
  <div class="coupon-manager">
    <el-card>
      <template #header><div style="display: flex; justify-content: space-between;"><span>🎫 领劵中心设置</span><el-button type="primary" :icon="Plus" @click="openAddCouponDialog">新建优惠券</el-button></div></template>
      <el-table :data="couponList" border stripe>
        <el-table-column prop="name" label="名称" />
        <el-table-column label="面额"><template #default="scope"><span style="color:#f56c6c;font-weight:bold;">¥{{scope.row.amount}}</span></template></el-table-column>
        <el-table-column label="门槛"><template #default="scope">{{scope.row.min_spend > 0 ? `满${scope.row.min_spend}元` : '无门槛'}}</template></el-table-column>
        <el-table-column label="领取限制"><template #default="scope"><el-tag :type="scope.row.limit_level === 1 ? 'info' : (scope.row.limit_level === 2 ? 'warning' : 'danger')">{{ getLevelName(scope.row.limit_level) }}</el-tag></template></el-table-column>
        <el-table-column prop="stock" label="剩余库存" />
        <el-table-column label="操作" width="150"><template #default="scope">
            <el-button size="small" type="primary" :icon="Edit" circle @click="openEditCoupon(scope.row)"></el-button>
            <el-button size="small" type="danger" :icon="Delete" circle @click="deleteCoupon(scope.row)"></el-button>
        </template></el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="couponDialogVisible" :title="isEditCoupon ? '编辑优惠券' : '新建优惠券'" width="500px">
        <el-form label-width="100px">
            <el-form-item label="优惠券名称"><el-input v-model="couponForm.name" placeholder="如：新人专享" /></el-form-item>
            <el-form-item label="优惠金额"><el-input-number v-model="couponForm.amount" :min="1" /> 元</el-form-item>
            <el-form-item label="使用门槛"><el-input-number v-model="couponForm.min_spend" :min="0" /> 元 (0为无门槛)</el-form-item>
            <el-form-item label="发放库存"><el-input-number v-model="couponForm.stock" :min="1" /> 张</el-form-item>
            <el-form-item label="领取限制">
                <el-select v-model="couponForm.limit_level" placeholder="请选择">
                    <el-option label="所有人可领" :value="1"></el-option>
                    <el-option label="仅限黄金VIP可领" :value="2"></el-option>
                    <el-option label="仅限钻石VIP可领" :value="3"></el-option>
                </el-select>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="couponDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitCoupon">保存</el-button>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

const couponList = ref([])
const couponDialogVisible = ref(false)
const isEditCoupon = ref(false)
const couponForm = reactive({ id: 0, name: '', amount: 10, min_spend: 0, limit_level: 1, stock: 100 })

const loadCoupons = async () => {
    try {
        const res = await axios.get('http://localhost:5000/api/admin/coupons');
        couponList.value = res.data.data
    } catch(e) { ElMessage.error('加载优惠券失败') }
}

const openAddCouponDialog = () => { isEditCoupon.value=false; Object.assign(couponForm, {name:'', amount:10, min_spend:0, limit_level:1, stock:100}); couponDialogVisible.value=true }
const openEditCoupon = (row) => { isEditCoupon.value=true; Object.assign(couponForm, row); couponDialogVisible.value=true }

const submitCoupon = async () => {
    if(!couponForm.name) return ElMessage.warning('请输入名称');
    try {
        if(isEditCoupon.value) await axios.put(`http://localhost:5000/api/admin/coupons/${couponForm.id}`, couponForm);
        else await axios.post('http://localhost:5000/api/admin/coupons', couponForm);
        couponDialogVisible.value = false;
        ElMessage.success('保存成功');
        loadCoupons();
    } catch(e) { ElMessage.error('操作失败') }
}

const deleteCoupon = (row) => {
    ElMessageBox.confirm('确认删除?').then(async()=>{
        try {
            await axios.delete(`http://localhost:5000/api/admin/coupons/${row.id}`);
            loadCoupons()
            ElMessage.success('删除成功')
        } catch(e) { ElMessage.error('删除失败') }
    }).catch(() => {})
}

const getLevelName = (level) => { return level===1?'所有人':(level===2?'黄金VIP':'💎 钻石VIP') }

onMounted(() => {
    loadCoupons()
})
</script>
