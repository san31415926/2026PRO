<template>
  <div>
    <el-card>
      <template #header><span>👥 会员列表</span></template>
      <el-table :data="memberList" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="头像" width="70">
          <template #default="scope"><el-avatar :size="36" :src="scope.row.avatar" /></template>
        </el-table-column>
        <el-table-column prop="username" label="账号" width="130" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column label="等级" width="110">
          <template #default="scope">
            <el-tag v-if="scope.row.level === 1" type="info">普通会员</el-tag>
            <el-tag v-else-if="scope.row.level === 2" style="background:#ffd700;border-color:#ffd700;color:#333;">黄金VIP</el-tag>
            <el-tag v-else type="primary">钻石VIP</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="余额" width="110">
          <template #default="scope"><span style="color:#f56c6c;font-weight:bold;">¥{{ scope.row.balance.toFixed(2) }}</span></template>
        </el-table-column>
        <el-table-column prop="points" label="积分" width="90" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" type="danger" plain @click="resetBalance(scope.row)">充值余额</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="rechargeVisible" title="管理员充值" width="360px">
      <div style="padding:10px 0;">
        <p>为 <b>{{ selectedMember?.nickname }}</b> 充值余额</p>
        <el-input-number v-model="rechargeAmount" :min="1" :max="99999" style="width:100%;margin-top:10px;" />
      </div>
      <template #footer>
        <el-button @click="rechargeVisible=false">取消</el-button>
        <el-button type="primary" @click="submitRecharge">确认充值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const memberList = ref([])
const rechargeVisible = ref(false)
const selectedMember = ref(null)
const rechargeAmount = ref(100)

const loadMembers = async () => {
  const res = await axios.get('http://localhost:5000/api/admin/members')
  if (res.data.code === 200) memberList.value = res.data.data
}

const resetBalance = (row) => {
  selectedMember.value = row
  rechargeAmount.value = 100
  rechargeVisible.value = true
}

const submitRecharge = async () => {
  const res = await axios.post('http://localhost:5000/api/admin/member/recharge', {
    user_id: selectedMember.value.id,
    amount: rechargeAmount.value
  })
  if (res.data.code === 200) {
    ElMessage.success('充值成功')
    rechargeVisible.value = false
    loadMembers()
  } else {
    ElMessage.error(res.data.msg || '操作失败')
  }
}

onMounted(loadMembers)
</script>
